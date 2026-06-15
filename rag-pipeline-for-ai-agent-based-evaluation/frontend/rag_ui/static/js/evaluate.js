/* ============================================================
   Evaluate page
   ============================================================ */

function toast(msg, type = 'info') {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.className = `toast toast-${type} show`;
    clearTimeout(el._t);
    el._t = setTimeout(() => {
        el.className = 'toast';
    }, 4000);
}

function getCsrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
}

function escHtml(str) {
    return String(str ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

// Built-in sample questions — mirrors sample_data/eval/sample_questions.json
const SAMPLE_QUESTIONS = [
    {
        question: "What paper introduced the Transformer architecture and in what year?",
        answer: "The Transformer was introduced in the 2017 paper 'Attention Is All You Need' by Vaswani et al."
    },
    {
        question: "What are the three vectors computed for each token in self-attention?",
        answer: "Query (Q), Key (K), and Value (V)."
    },
    {
        question: "What is the difference between encoder-only and decoder-only transformer models?",
        answer: "Encoder-only models use bidirectional attention and are good for classification. Decoder-only models use causal attention for text generation."
    },
    {
        question: "What is Chain-of-Thought prompting and how do you trigger it zero-shot?",
        answer: "CoT encourages step-by-step reasoning. Zero-shot CoT is triggered by adding 'Let's think step by step.' to the prompt."
    },
    {
        question: "What is RAG and what problem does it solve?",
        answer: "RAG enhances LLM responses by retrieving relevant information from an external knowledge base. It solves outdated knowledge, hallucination, and lack of private data."
    },
    {
        question: "What vector database is used in this project and why?",
        answer: "LanceDB — lightweight, file-based, great for local and serverless use."
    },
    {
        question: "What is HyDE in the context of RAG?",
        answer: "HyDE generates a hypothetical answer, embeds it, and uses it to search the vector DB for more relevant chunks."
    },
    {
        question: "What is temperature in LLM inference?",
        answer: "Temperature controls the sharpness of the probability distribution. Temperature 0 gives greedy decoding; higher values give more random outputs."
    },
    {
        question: "What is overfitting and how can it be prevented?",
        answer: "Overfitting is when a model memorises training data and performs poorly on new data. Prevented with L1/L2 regularisation, dropout, and early stopping."
    },
    {
        question: "What activation function is most commonly used in neural networks?",
        answer: "ReLU (Rectified Linear Unit), formula: max(0, x)."
    },
];

let questions = null;

const evalFileInput = document.getElementById('eval-file-input');
const evalUploadZone = document.getElementById('eval-upload-zone');
const btnLoadSampleEval = document.getElementById('btn-load-sample-eval');
const btnRunEval = document.getElementById('btn-run-eval');
const scoreCard = document.getElementById('score-card');
const scoreNumber = document.getElementById('score-number');
const scoreBar = document.getElementById('score-bar');
const scorePct = document.getElementById('score-pct');
const resultsWrap = document.getElementById('results-wrap');
const resultsBody = document.getElementById('results-body');
const evalSpinner = document.getElementById('eval-spinner');

function setUploadLabel(text) {
    evalUploadZone.querySelector('.upload-text').textContent = text;
}

// Upload JSON file
evalUploadZone.addEventListener('click', () => evalFileInput.click());

evalFileInput.addEventListener('change', () => {
    const file = evalFileInput.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
        try {
            questions = JSON.parse(e.target.result);
            if (!Array.isArray(questions) || !questions[0]?.question) {
                throw new Error('Expected [{question, answer}, …]');
            }
            toast(`Loaded ${questions.length} questions from ${file.name}`, 'success');
            btnRunEval.disabled = false;
            setUploadLabel(`${file.name} — ${questions.length} questions loaded`);
        } catch (err) {
            toast('Invalid JSON: ' + err.message, 'error');
            questions = null;
            btnRunEval.disabled = true;
        }
    };
    reader.readAsText(file);
});

// Drag and drop
evalUploadZone.addEventListener('dragover', e => {
    e.preventDefault();
    evalUploadZone.classList.add('drag-over');
});
evalUploadZone.addEventListener('dragleave', () => evalUploadZone.classList.remove('drag-over'));
evalUploadZone.addEventListener('drop', e => {
    e.preventDefault();
    evalUploadZone.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) {
        // Assign to input and fire change
        evalFileInput.files = e.dataTransfer.files;
        evalFileInput.dispatchEvent(new Event('change'));
    }
});

// Load built-in sample
btnLoadSampleEval.addEventListener('click', () => {
    questions = SAMPLE_QUESTIONS;
    btnRunEval.disabled = false;
    setUploadLabel(`Sample questions loaded — ${questions.length} questions`);
    toast(`Loaded ${questions.length} sample questions`, 'info');
});

// Run evaluation
btnRunEval.addEventListener('click', async () => {
    if (!questions?.length) return;

    // Reset UI state
    btnRunEval.disabled = true;
    btnLoadSampleEval.disabled = true;
    scoreCard.hidden = true;
    resultsWrap.hidden = true;
    evalSpinner.hidden = false;
    resultsBody.innerHTML = '';

    try {
        const res = await fetch('/api/evaluate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrf(),
            },
            body: JSON.stringify({questions}),
        });

        evalSpinner.hidden = true;
        const data = await res.json();

        if (!res.ok) {
            toast('❌ ' + (data.detail || 'Evaluation failed'), 'error');
            return;
        }

        // Animate score bar
        const pct = data.total > 0 ? (data.score / data.total) * 100 : 0;
        scoreNumber.textContent = `${data.score} / ${data.total}`;
        scorePct.textContent = pct.toFixed(1) + '% accuracy';
        scoreCard.hidden = false;
        // Trigger CSS transition on next frame
        requestAnimationFrame(() => {
            scoreBar.style.width = pct.toFixed(1) + '%';
        });

        // Populate results table
        data.results.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
        <td class="col-status">
          <span class="${r.is_correct ? 'status-pass' : 'status-fail'}">
            ${r.is_correct ? '✓' : '✗'}
          </span>
        </td>
        <td class="col-question">${escHtml(r.question)}</td>
        <td class="col-response">${escHtml(r.response)}</td>
        <td class="col-expected">${escHtml(r.expected_answer)}</td>
        <td class="col-reasoning">${escHtml(r.reasoning ?? '—')}</td>
      `;
            resultsBody.appendChild(tr);
        });
        resultsWrap.hidden = false;

        const toastType = pct >= 70 ? 'success' : pct >= 40 ? 'info' : 'error';
        toast(`Evaluation complete — ${data.score}/${data.total} correct (${pct.toFixed(1)}%)`, toastType);

    } catch {
        evalSpinner.hidden = true;
        toast('❌ Backend unreachable or request timed out', 'error');
    } finally {
        btnRunEval.disabled = false;
        btnLoadSampleEval.disabled = false;
    }
});
