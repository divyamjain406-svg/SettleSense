"""
SettleSense — Settlement Exception Investigation Copilot.
Offline LLM-based financial operations dashboard powered by Streamlit,
scikit-learn, ChromaDB, and local Ollama models (qwen3:4b, nomic-embed-text).
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import json
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import streamlit as st
import pandas as pd
from PIL import Image

from config.settings import (
    DATA_DIR,
    RESULTS_DIR,
    FIGURES_DIR,
    KNOWLEDGE_BASE_DIR,
    CANONICAL_CATEGORIES,
    AMBIGUOUS_LABEL,
    OLLAMA_BASE_URL,
    OLLAMA_GEN_MODEL,
    OLLAMA_EMBED_MODEL,
)
from src.train_classifier import SettlementClassifier
from src.semantic_retrieval import SemanticRetriever
from src.rag_pipeline import SettleSenseRAGPipeline
from src.ollama_client import OllamaClient
from src.lexical_retrieval import load_procedure_documents
from src.evaluation import extract_metric_value, format_kpi_value

# Streamlit Page Config
st.set_page_config(
    page_title="SettleSense — Settlement Exception Copilot",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Financial Operations Dashboard
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .status-badge-ok {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-badge-warn {
        background-color: #FEF08A;
        color: #854D0E;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-badge-err {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .metric-card {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        padding: 14px;
        border-radius: 8px;
        text-align: center;
    }
    .report-box {
        background: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-left: 5px solid #2563EB;
        border-radius: 6px;
        padding: 18px;
        margin-top: 15px;
    }
    .banner-mandatory-review {
        background-color: #FEE2E2 !important;
        border-left: 5px solid #DC2626 !important;
        color: #7F1D1D !important;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 15px;
        font-weight: 500;
        line-height: 1.5;
    }
    .banner-mandatory-review * {
        color: #7F1D1D !important;
    }
    .banner-standard-review {
        background-color: #ECFDF5 !important;
        border-left: 5px solid #059669 !important;
        color: #064E3B !important;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 15px;
        font-weight: 500;
        line-height: 1.5;
    }
    .banner-standard-review * {
        color: #064E3B !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_classifier():
    return SettlementClassifier()

@st.cache_resource
def get_ollama_client():
    return OllamaClient()

@st.cache_resource
def get_rag_pipeline():
    return SettleSenseRAGPipeline()

@st.cache_data
def load_sample_cases():
    sample_file = DATA_DIR / "sample_cases.json"
    if sample_file.exists():
        with open(sample_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@st.cache_data
def load_procedures():
    return load_procedure_documents(KNOWLEDGE_BASE_DIR)


# Sidebar: System Health, Model Status, and Boundaries
with st.sidebar:
    st.image("https://img.icons8.com/color/96/bank-building.png", width=56)
    st.markdown("### **SettleSense Copilot**")
    st.caption("Offline Securities Settlement Exception Copilot")

    st.markdown("---")
    st.markdown("#### **Local Model Health**")

    client = get_ollama_client()
    health = client.check_health()

    if health["reachable"]:
        st.markdown("**Ollama Service:** <span class='status-badge-ok'>CONNECTED</span>", unsafe_allow_html=True)
        st.caption(f"Host: `{OLLAMA_BASE_URL}`")

        # Generation model
        if health["gen_model_available"]:
            st.markdown(f"**LLM:** `{OLLAMA_GEN_MODEL}` <span class='status-badge-ok'>READY</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**LLM:** `{OLLAMA_GEN_MODEL}` <span class='status-badge-err'>MISSING</span>", unsafe_allow_html=True)
            st.info(f"Install command:\n```bash\nollama pull {OLLAMA_GEN_MODEL}\n```")

        # Embedding model
        if health["embed_model_available"]:
            st.markdown(f"**Embedder:** `{OLLAMA_EMBED_MODEL}` <span class='status-badge-ok'>READY</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**Embedder:** `{OLLAMA_EMBED_MODEL}` <span class='status-badge-err'>MISSING</span>", unsafe_allow_html=True)
            st.info(f"Install command:\n```bash\nollama pull {OLLAMA_EMBED_MODEL}\n```")
    else:
        st.markdown("**Ollama Service:** <span class='status-badge-err'>UNREACHABLE</span>", unsafe_allow_html=True)
        st.warning(
            "Local Ollama daemon is offline.\n\n"
            "Classifier predictions remain active.\n"
            "To enable RAG, launch Ollama: `ollama serve`"
        )

    # Vector Store Health
    pipeline = get_rag_pipeline()
    if pipeline.semantic_retriever.is_ready:
        v_count = pipeline.semantic_retriever.vector_index.collection.count()
        st.markdown(f"**Vector Store:** <span class='status-badge-ok'>{v_count} PASSAGES</span>", unsafe_allow_html=True)
    else:
        st.markdown("**Vector Store:** <span class='status-badge-warn'>NOT INDEXED</span>", unsafe_allow_html=True)
        st.caption("Run `python scripts/build_index.py`")

    st.markdown("---")
    st.markdown("#### **Operational Boundaries**")
    st.info(
        "**Educational Prototype**\n\n"
        "- Purely synthetic exception cases & illustrative procedures.\n"
        "- No live exchange or custody connection.\n"
        "- Zero external or cloud API calls.\n"
        "- Investigation report is an analyst aid; not a confirmed root-cause.\n"
        "- Human verification is mandatory."
    )


# Header
st.markdown("<div class='main-header'>SettleSense — Settlement Exception Investigation Copilot</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Offline AI Investigation Support Using NLP, Semantic Retrieval & Retrieval-Augmented Generation</div>", unsafe_allow_html=True)

# Main Navigation Tabs
tab_investigate, tab_knowledge_base, tab_evaluation = st.tabs([
    "🔍 Exception Investigation",
    "📚 Procedure Knowledge Base",
    "📊 Benchmarks & Evaluation",
])

# -------------------------------------------------------------------------
# TAB 1: EXCEPTION INVESTIGATION
# -------------------------------------------------------------------------
with tab_investigate:
    sample_cases = load_sample_cases()

    col_load, col_info = st.columns([2, 1])
    with col_load:
        sample_options = ["-- Select Pre-Loaded Example Case --"] + [s["label_preview"] for s in sample_cases]
        selected_sample_idx = st.selectbox(
            "Quick Load Example Case (Covers 6 Categories & Ambiguous Cases):",
            range(len(sample_options)),
            format_func=lambda i: sample_options[i]
        )

    default_case_id = "SS-MANUAL-01"
    default_desc = ""
    default_trade_type = "EQUITY_DVP"
    default_status = "REJECTED_CSD"
    default_code = "EXC_MANUAL_100"

    if selected_sample_idx > 0:
        chosen = sample_cases[selected_sample_idx - 1]
        default_case_id = chosen["case_id"]
        default_desc = chosen["case_description"]
        default_trade_type = chosen.get("trade_type", "EQUITY_DVP")
        default_status = chosen.get("transaction_status", "REJECTED_CSD")
        default_code = chosen.get("exception_code", "EXC_100")

    with st.form("investigation_form"):
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            case_id_input = st.text_input("Synthetic Case ID:", value=default_case_id)
        with col_c2:
            trade_type_input = st.text_input("Trade Settlement Type:", value=default_trade_type)
        with col_c3:
            status_input = st.text_input("Transaction Status:", value=default_status)
        with col_c4:
            code_input = st.text_input("Exception Code:", value=default_code)

        desc_input = st.text_area(
            "Settlement Exception Narrative / Custodian Advice Text:",
            value=default_desc,
            height=140,
            placeholder="Enter operational settlement failure description..."
        )

        submitted = st.form_submit_button("🚀 Run Dual-Engine Investigation", use_container_width=True)

    if submitted:
        if not desc_input.strip():
            st.error("Please provide an exception narrative to investigate.")
        else:
            st.markdown("---")
            st.subheader("Investigation Results")

            # Dual Engine Row
            col_left, col_right = st.columns([1, 1])

            # 1. Supervised NLP Classifier (Approach A)
            with col_left:
                st.markdown("#### **Engine 1: Traditional NLP Classifier**")
                classifier = get_classifier()
                if classifier.is_ready:
                    pred = classifier.predict(desc_input)
                    cat = pred["predicted_category"]
                    conf = pred["confidence"]

                    badge_class = "status-badge-ok" if conf > 0.60 else "status-badge-warn"
                    st.markdown(
                        f"**Candidate Category:** <span class='{badge_class}'>{cat}</span> "
                        f"(Confidence: **{conf:.1%}**)",
                        unsafe_allow_html=True
                    )

                    with st.expander("View Category Probability Distribution"):
                        prob_df = pd.DataFrame(
                            list(pred["probabilities"].items()),
                            columns=["Category", "Probability"]
                        ).sort_values(by="Probability", ascending=False)
                        st.dataframe(prob_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("Classifier models not found. Run `python src/train_classifier.py`.")

            # 2. Retrieved Procedure Evidence (Approach B & D)
            with col_right:
                st.markdown("#### **Engine 2: Retrieved Procedure Excerpts**")
                pipeline = get_rag_pipeline()
                retrieved_passages = []
                if pipeline.semantic_retriever.is_ready:
                    retrieved_passages = pipeline.semantic_retriever.retrieve(desc_input, top_k=3)
                    if retrieved_passages:
                        for p in retrieved_passages:
                            st.markdown(
                                f"**[{p['procedure_id']}] {p['title']}** "
                                f"*(Sim: `{p['similarity_score']:.2f}` | Category: `{p['category']}`)*"
                            )
                            with st.expander(f"Inspect Excerpt for {p['procedure_id']}"):
                                st.text(p["excerpt"])
                    else:
                        st.info("No matching procedures retrieved above similarity threshold.")
                else:
                    st.warning("Procedure vector store not indexed. Run `python scripts/build_index.py`.")

            st.markdown("---")
            # 3. Grounded Copilot Investigation Report (Approach D)
            st.markdown("### **Structured Copilot Investigation Report**")

            with st.spinner("Generating grounded investigation report with local LLM (qwen3:4b)..."):
                result = pipeline.run_rag(
                    case_description=desc_input,
                    case_id=case_id_input,
                    trade_type=trade_type_input,
                    transaction_status=status_input,
                    exception_code=code_input,
                    top_k=3
                )

            report = result["report"]
            val = result["validation"]

            if report:
                # Escalation Banner
                if report.requires_human_review:
                    st.markdown(
                        "<div class='banner-mandatory-review' style='background-color:#FEE2E2 !important;border-left:5px solid #DC2626 !important;color:#7F1D1D !important;padding:12px 16px;border-radius:4px;margin-bottom:15px;font-weight:500;line-height:1.5;'>"
                        "<strong style='color:#7F1D1D !important;'>⚠️ MANDATORY HUMAN REVIEW REQUIRED:</strong> "
                        "<span style='color:#7F1D1D !important;'>This exception exhibits operational uncertainty, potential discrepancy, or requires manual confirmation before resolution.</span>"
                        "</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        "<div class='banner-standard-review' style='background-color:#ECFDF5 !important;border-left:5px solid #059669 !important;color:#064E3B !important;padding:12px 16px;border-radius:4px;margin-bottom:15px;font-weight:500;line-height:1.5;'>"
                        "<strong style='color:#064E3B !important;'>✅ STANDARD REVIEW:</strong> "
                        "<span style='color:#064E3B !important;'>Routine exception alignment. Analyst verification of procedure checks recommended.</span>"
                        "</div>",
                        unsafe_allow_html=True
                    )

                # Report Card
                st.markdown(f"**Case Summary:** {report.case_summary}")

                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    st.markdown(f"**Candidate Category:** `{report.candidate_failure_category}`")
                with col_r2:
                    st.markdown(f"**Confidence Level:** `{report.category_confidence_or_uncertainty}`")
                with col_r3:
                    st.markdown(f"**Report Latency:** `{result['latency_seconds']} s`")

                col_ev, col_cause = st.columns(2)
                with col_ev:
                    st.markdown("#### **Supporting Evidence (Observed Facts)**")
                    for ev in report.supporting_evidence:
                        st.markdown(f"- {ev}")
                with col_cause:
                    st.markdown("#### **Possible Causes (Hypotheses)**")
                    for cause in report.possible_causes:
                        st.markdown(f"- *{cause}*")

                col_chk, col_miss = st.columns(2)
                with col_chk:
                    st.markdown("#### **Recommended Verification Checks**")
                    for chk in report.recommended_checks:
                        st.markdown(f"- [ ] {chk}")
                with col_miss:
                    st.markdown("#### **Missing Information to Collect**")
                    if report.missing_information:
                        for miss in report.missing_information:
                            st.markdown(f"- ❓ {miss}")
                    else:
                        st.markdown("- None identified.")

                st.markdown("#### **Cited Procedure References**")
                if report.procedure_references:
                    cite_badges = []
                    for cite in report.procedure_references:
                        if cite in val.valid_citations:
                            cite_badges.append(f"<span class='status-badge-ok'>✓ {cite}</span>")
                        else:
                            cite_badges.append(f"<span class='status-badge-err'>⚠️ Invalid: {cite}</span>")
                    st.markdown(" ".join(cite_badges), unsafe_allow_html=True)
                else:
                    st.markdown("*(No procedure references cited)*")

                st.markdown(f"**Investigation Note:**\n> {report.investigation_note}")

                # Audit View
                with st.expander("🛠️ View Raw JSON Report & Validation Details"):
                    st.json(report.model_dump())
                    st.markdown(f"**Citation Validity Rate:** `{val.citation_validity_rate:.1%}`")
                    if val.validation_errors:
                        st.error(f"Validation Warnings: {val.validation_errors}")


# -------------------------------------------------------------------------
# TAB 2: PROCEDURE KNOWLEDGE BASE BROWSER
# -------------------------------------------------------------------------
with tab_knowledge_base:
    st.subheader("Illustrative Settlement Procedures Library")
    st.caption("14 synthetic operational procedure documents indexed for semantic and lexical retrieval.")

    procedures = load_procedures()
    for proc in procedures:
        with st.expander(f"[{proc['procedure_id']}] {proc['title']} — Category: {proc['category']}"):
            st.markdown(f"**Source Type:** `{proc['source_type']}` | **File:** `{proc['file_name']}`")
            st.markdown("---")
            st.markdown(proc["raw_text"])


# -------------------------------------------------------------------------
# TAB 3: BENCHMARKS & EVALUATION DASHBOARD
# -------------------------------------------------------------------------
with tab_evaluation:
    st.subheader("Empirical Experimental Evaluation & Benchmark Results")
    st.caption("Offline benchmark metrics computed across all four experimental approaches.")

    metrics_csv = RESULTS_DIR / "metrics.csv"
    comp_csv = RESULTS_DIR / "comparison_table.csv"

    if metrics_csv.exists() and comp_csv.exists():
        metrics_df = pd.read_csv(metrics_csv)
        comp_df = pd.read_csv(comp_csv)

        metrics_dict = dict(zip(metrics_df["Metric"], metrics_df["Value"]))
        clf_acc = extract_metric_value(metrics_dict, [
            "Classifier Accuracy (Held-out Test Split)",
            "Classifier Accuracy",
            "Approach A Accuracy"
        ])
        clf_f1 = extract_metric_value(metrics_dict, [
            "Classifier Macro-F1 (Held-out Test Split)",
            "Classifier Macro-F1",
            "Approach A Macro-F1"
        ])
        lex_hit3 = extract_metric_value(metrics_dict, [
            "Lexical Retrieval Hit@3 (Labelled Cases)",
            "Lexical Retrieval Hit@3",
            "Approach B Hit@3"
        ])
        lex_mrr = extract_metric_value(metrics_dict, [
            "Lexical Retrieval MRR",
            "Approach B MRR"
        ])
        sem_hit3 = extract_metric_value(metrics_dict, [
            "Semantic Retrieval Hit@3 (Labelled Cases)",
            "Semantic Retrieval Hit@3",
            "Approach D Hit@3"
        ])
        sem_mrr = extract_metric_value(metrics_dict, [
            "Semantic Retrieval MRR",
            "Approach D MRR"
        ])
        unc_esc = extract_metric_value(metrics_dict, [
            "Ambiguous Cases Human Escalation Rate",
            "Uncertainty Human Review Escalation Rate",
            "Approach D Human Escalation Rate"
        ])
        unc_guardrail = extract_metric_value(metrics_dict, [
            "Ambiguous Cases Non-Definitive / Low Confidence",
            "Uncertainty Low Confidence / Non-Definitive",
            "Low Confidence / Non-Definitive"
        ])

        # Top Metric KPI Cards (Dynamic with explicit denominators)
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric(
                "Approach A: Classifier Accuracy",
                format_kpi_value(clf_acc, "{:.2%}"),
                f"Macro-F1: {format_kpi_value(clf_f1, '{:.3f}')} (N=55)"
            )
        with kpi2:
            st.metric(
                "Approach B: Lexical Hit@3",
                format_kpi_value(lex_hit3, "{:.2%}"),
                f"MRR: {format_kpi_value(lex_mrr, '{:.3f}')} (N=210)"
            )
        with kpi3:
            st.metric(
                "Approach D: Semantic Hit@3",
                format_kpi_value(sem_hit3, "{:.2%}"),
                f"MRR: {format_kpi_value(sem_mrr, '{:.3f}')} (N=210)"
            )
        with kpi4:
            guard_delta = f" | Guardrail: {format_kpi_value(unc_guardrail, '{:.0%}')} (N=30)" if unc_guardrail is not None else ""
            st.metric(
                "Uncertainty Escalation Rate",
                format_kpi_value(unc_esc, "{:.1%}"),
                f"Pilot: N=2{guard_delta}"
            )

        st.markdown("---")
        st.markdown("#### **Approach Comparison Matrix**")
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### **Evaluation Visualizations**")

        f_col1, f_col2 = st.columns(2)
        with f_col1:
            fig1 = FIGURES_DIR / "class_distribution.png"
            if fig1.exists():
                st.image(str(fig1), caption="Figure 1: Dataset Class Distribution (N=240)", use_container_width=True)

            fig3 = FIGURES_DIR / "macro_f1_comparison.png"
            if fig3.exists():
                st.image(str(fig3), caption="Figure 3: Categorization Macro-F1 Across Approaches", use_container_width=True)

            fig5 = FIGURES_DIR / "response_latency_comparison.png"
            if fig5.exists():
                st.image(str(fig5), caption="Figure 5: Mean Component Response Latency (ms)", use_container_width=True)

        with f_col2:
            fig2 = FIGURES_DIR / "confusion_matrix.png"
            if fig2.exists():
                st.image(str(fig2), caption="Figure 2: Approach A Classifier Confusion Matrix", use_container_width=True)

            fig4 = FIGURES_DIR / "retrieval_hit3_comparison.png"
            if fig4.exists():
                st.image(str(fig4), caption="Figure 4: Procedure Retrieval Comparison (Hit@3, Recall@3, MRR)", use_container_width=True)

            fig6 = FIGURES_DIR / "uncertainty_handling.png"
            if fig6.exists():
                st.image(str(fig6), caption="Figure 6: Handling of 30 Ambiguous Settlement Cases", use_container_width=True)

    else:
        st.warning("Evaluation artifacts not found. Please run `python scripts/run_experiments.py`.")

