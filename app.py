"""Run: python -m streamlit run app.py"""
import io
import json
import zipfile
import streamlit as st
from analysis import prepare_image, make_prompt, fingerprint, interpret

st.set_page_config(page_title='Omics Plot Workbench', page_icon='🧬', layout='wide')
st.markdown('''<style>
.block-container{max-width:1320px;padding-top:2rem}
h1{letter-spacing:-1.3px} h3{font-weight:600}
[data-testid="stMetric"]{background:white;border:1px solid #dfE7ef;border-radius:14px;padding:16px}
.eyebrow{color:#087e8b;font-size:.8rem;letter-spacing:2px;font-weight:700}
.intro{color:#627588;font-size:1.1rem;max-width:780px}
</style>''', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('### 🧬 Omics Workbench')
    st.caption('FROM FIGURES TO UNDERSTANDING')
    st.divider()
    mode = st.radio('Interpretation mode', ['ChatGPT prompt · no API key', 'Automatic AI interpretation'])
    provider = 'OpenAI'
    key = ''
    model = 'gpt-4.1'
    if mode.startswith('Automatic'):
        provider = st.selectbox('AI provider', ['Google Gemini', 'OpenAI'])
        if provider == 'Google Gemini':
            key = st.text_input('Gemini API key', type='password', key='gemini_api_key')
            model = st.text_input('Gemini vision model', value='gemini-2.5-flash', key='gemini_model')
            st.markdown('[Get a Gemini key](https://aistudio.google.com/apikey)')
            st.caption('Free-tier usage is available for eligible accounts, with limits. Billing-enabled projects may incur charges. Your key is excluded from exports.')
        else:
            key = st.text_input('OpenAI API key', type='password', key='openai_api_key')
            model = st.text_input('OpenAI vision model', value='gpt-4.1', key='openai_model')
            st.caption('API use is billed separately. Your key is excluded from exports.')
    st.divider()
    st.markdown('**Your workflow**\n\n1. Add study context\n2. Upload & label figures\n3. Interpret & review\n4. Download your report')
    if st.button('Clear workspace', width='stretch'):
        st.session_state.clear()
        st.rerun()

st.markdown('<div class="eyebrow">BIOINFORMATICS / FIGURE INTERPRETATION</div>', unsafe_allow_html=True)
st.title('Understand the patterns in your data')
st.caption('Version 1.1 · Gemini + OpenAI')
st.markdown('<p class="intro">Upload PCA plots and heatmaps. Add the context behind your experiment. Build a clear interpretation, Results paragraph, and figure captions.</p>', unsafe_allow_html=True)
st.caption('Interprets existing figures. Calculating PCA, differential expression, and statistics requires the underlying data.')

study_tab, figures_tab, report_tab, learn_tab = st.tabs(['01  Study details', '02  Figures', '03  Interpretation & report', 'Learn the terms'])
with study_tab:
    st.subheader('Tell the story behind your figures')
    st.caption('Leave unknown details blank. Missing information will be flagged in the interpretation.')
    title = st.text_input('Study title', placeholder='For example: treatment response in two cell types')
    a, b = st.columns(2)
    with a:
        dtype = st.selectbox('Data type', ['Unknown', 'RNA-seq', 'Proteomics', 'Other'])
        groups = st.text_area('Sample groups and label mapping', placeholder='Which sample names belong to which group?')
        treatment = st.text_area('Treatment or condition', placeholder='Treatment, dose, duration, cell types, or tissue')
        replicates = st.text_input('Biological replicates per group', placeholder='Example: control = 3, treated = 3; or unknown')
    with b:
        normalization = st.text_input('Normalization', placeholder='Example: CPM, TPM, DESeq2; leave blank if unknown')
        transform = st.text_input('Transformation', placeholder='Example: log2(CPM + 1), VST')
        selection = st.text_input('Heatmap gene/protein selection', placeholder='Example: 20 most variable genes')
        scaling = st.selectbox('Heatmap scaling', ['Unknown', 'Row z-score', 'Column z-score', 'Unscaled expression values', 'Other (describe below)'])
        scale_notes = st.text_input('Color legend / scaling details', placeholder='Legend limits, units, meaning of colors')
    other = st.text_area('Other context', placeholder='Batch information, PCA feature selection/scaling, technical replicates, known QC concerns…')
    study = {'title': title, 'data_type': dtype, 'groups': groups, 'condition': treatment,
             'biological_replicates': replicates, 'normalization': normalization,
             'transformation': transform, 'heatmap_selection': selection,
             'heatmap_scaling': scaling, 'legend_details': scale_notes, 'other_context': other}

figures = []
with figures_tab:
    st.subheader('Bring your figures into focus')
    st.caption('PNG, JPG, JPEG, or WEBP · up to 6 figures · 15 MB per image. Export PDF/TIFF plots as PNG first.')
    uploads = st.file_uploader('Upload PCA plots and heatmaps', type=['png','jpg','jpeg','webp'], accept_multiple_files=True)
    if len(uploads) > 6:
        st.error('Please select at most 6 figures. Extra files will not be included.')
    for i, file in enumerate(uploads[:6]):
        try:
            png, size = prepare_image(file.getvalue())
            import hashlib
            widget_id = f'{i}_{hashlib.sha256(file.getvalue()).hexdigest()[:12]}'
            with st.container(border=True):
                left, right = st.columns([2, 1])
                with left:
                    st.image(png, caption=f'Figure {i+1} · {file.name}', width='stretch')
                with right:
                    kind = st.selectbox('Figure type', ['PCA', 'Heatmap', 'Other / unsure'], key='kind_'+widget_id)
                    notes = st.text_area('Notes / readable label corrections', key='notes_'+widget_id,
                                         placeholder='Optional: PC1 %, sample labels, what the legend says…')
                    st.caption(f'{size[0]} × {size[1]} pixels')
                    if min(size) < 600:
                        st.warning('Small image: labels may be hard to read. Upload a larger export if possible.')
            figures.append({'name': file.name, 'kind': kind, 'notes': notes, 'png': png})
        except Exception as exc:
            st.error(f'{file.name}: Unable to read this image. {exc}')
    if not uploads:
        st.info('Start by uploading your figures. Your plots will appear here with individual labels and notes.')

prompt = make_prompt(study, figures)
current = fingerprint(prompt, figures)
with report_tab:
    c1, c2, c3 = st.columns(3)
    c1.metric('Figures ready', len(figures))
    c2.metric('PCA plots', sum(f['kind']=='PCA' for f in figures))
    c3.metric('Heatmaps', sum(f['kind']=='Heatmap' for f in figures))
    st.subheader('Build an evidence-based interpretation')
    if not figures:
        st.info('Upload at least one figure in the Figures tab to begin.')
    if mode.startswith('Automatic'):
        st.caption(f'Clicking Interpret sends the uploaded figures and study details to {provider}. No API request occurs just by uploading.')
        if st.button('Interpret my figures', type='primary', disabled=not figures or not key.strip() or not model.strip()):
            try:
                with st.spinner('Reading figures and preparing your report…'):
                    result = interpret(prompt, figures, key, model.strip(), provider=provider)
                st.session_state['report'] = result
                st.session_state['report_source'] = current
                st.session_state['report_editor'] = result
            except Exception as exc:
                st.error(str(exc))
        if not key.strip():
            st.info('Enter an API key in the sidebar, or choose ChatGPT prompt mode.')
    else:
        st.markdown('**Use your existing ChatGPT conversation**\n\nCopy the prompt below, upload the same figures to ChatGPT, then paste its answer into the report editor.')
        with st.expander('Ready-to-copy interpretation prompt', expanded=bool(figures)):
            st.code(prompt, language=None)
        st.download_button('Download interpretation prompt', prompt, 'interpretation_prompt.txt', disabled=not figures)

    stale = bool(st.session_state.get('report_source') and st.session_state['report_source'] != current)
    if stale:
        st.warning('The figures or study details have changed. The report below belongs to the earlier inputs; regenerate it or review it before exporting.')
    edited = st.text_area('Report editor — paste an answer or revise the AI draft', height=440, key='report_editor',
                          placeholder='Your interpretation, Results paragraph, and captions go here.')
    if edited:
        if stale and st.button('I have reviewed and updated the report for these inputs'):
            st.session_state['report_source'] = current
            st.rerun()
        with st.expander('Formatted report preview', expanded=True):
            st.markdown(edited)
        export = '# Omics Plot Workbench report\n\n' + edited + '\n\n## Supplied study details\n\n'
        export += '\n'.join(f'- **{k.replace("_", " ")}:** {v or "Not provided"}' for k,v in study.items())
        export += '\n\n## Figure inventory\n\n' + '\n'.join(f'- Figure {i+1}: {f["name"]} ({f["kind"]}); notes: {f["notes"] or "None"}' for i,f in enumerate(figures))
        st.download_button('Download report (.md)', export, 'omics_interpretation.md', mime='text/markdown', disabled=stale)
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('report.md', export)
            z.writestr('study_details.json', json.dumps(study, indent=2))
            z.writestr('interpretation_prompt.txt', prompt)
            for i, f in enumerate(figures):
                z.writestr(f'figure_{i+1}.png', f['png'])
        st.download_button('Download report + figures (.zip)', archive.getvalue(), 'omics_report_bundle.zip', mime='application/zip', disabled=stale)
    st.caption('Review the report before using it in research. Figures alone cannot establish significance, differential expression, pathway activation, or causation. Download your work before closing the app.')

with learn_tab:
    st.subheader('A few terms, in plain English')
    for term, explanation in {
        'PCA': 'Principal component analysis compresses many gene or protein measurements into a few summary axes. Each dot usually represents a sample; check the figure labels.',
        'PC1 and PC2': 'PC1 captures the largest share of variation in the processed data. PC2 captures the next largest, independent share. Their percentages describe variation represented, not treatment effect or accuracy.',
        'Biological replicates': 'Independent biological samples in the same group. Repeated measurements of the same sample are technical replicates.',
        'Heatmap': 'A table displayed with colors. Rows often represent genes/proteins and columns samples; the legend determines what colors mean.',
        'Row z-score': 'Each gene is centered and scaled across samples. Positive values are above that gene’s average; negative values are below. Colors do not compare absolute abundance across different genes.',
        'Batch effect': 'Variation related to processing date, instrument, or laboratory rather than the biological question.',
        'Outlier': 'A sample with an unusual pattern. Check its identity and quality before deciding whether to exclude it.',
        'Normalization and transformation': 'Normalization adjusts measurements for systematic differences such as library size. Transformation changes the numerical scale, often reducing the influence of very large values.'
    }.items():
        with st.expander(term):
            st.write(explanation)
