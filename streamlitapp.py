import streamlit as st
from pubmed import search_pmc, fetch_pmc_xml, extract_metadata
import xml.etree.ElementTree as ET

st.set_page_config(page_title="EEG Paper Finder", layout="wide")

st.title("🔎 EEG Visual Oddball Paper Search")
keywords = st.text_input("Enter search keywords", "EEG, visual oddball")

if st.button("Search PMC"):
    with st.spinner("Searching..."):
        keyword_list = [k.strip() for k in keywords.split(",")]
        pmc_ids = search_pmc(keyword_list)

    if not pmc_ids:
        st.warning("No PMC articles found.")
    else:
        st.success(f"Found {len(pmc_ids)} articles.")
        for pmc_id in pmc_ids:
            with st.spinner(f"Fetching PMC ID {pmc_id}..."):
                xml = fetch_pmc_xml(pmc_id)
                if not xml:
                    st.error(f"❌ Could not fetch full text for {pmc_id}")
                    continue
                root = ET.fromstring(xml)
                meta = extract_metadata(root, pmc_id)
                st.markdown("---")
                st.markdown(f"**PMCID:** {meta['PMCID']}")
                st.markdown(f"**Title:** {meta['title']}")
                st.markdown(f"**Year:** {meta['year']}")
                st.markdown(f"**Authors:** {meta['authors']}")
