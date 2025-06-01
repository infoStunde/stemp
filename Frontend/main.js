const backend = document.querySelector('meta[name="backend-url"]').content;

class PdfStampApp {
    constructor() {
        this.selectedPdf = null;
        this.stampText = document.getElementById('stampText').value;

        this.initEventListeners();
        this.refreshList();
    }

    initEventListeners() {
        document.getElementById('uploadForm').addEventListener('submit', e => this.uploadFile(e));
        document.getElementById('stampText').addEventListener('input', e => {
            this.stampText = e.target.value;
            if (this.selectedPdf) this.showPreview(this.selectedPdf);
        });
    }

    async refreshList() {
        const res = await fetch(`${backend}/files`);
        const files = await res.json();
        const ul = document.getElementById('pdfList');
        ul.innerHTML = '';
        files.forEach(file => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            li.textContent = file;
            li.style.cursor = 'pointer';
            li.onclick = () => this.showPreview(file);
            ul.appendChild(li);
        });
    }

    async uploadFile(e) {
        e.preventDefault();
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];
        if (!file) return;

        const data = new FormData();
        data.append('file', file);

        await fetch(`${backend}/upload`, { method: 'POST', body: data });
        this.refreshList();
        fileInput.value = '';
    }

    showPreview(filename) {
        this.selectedPdf = filename;
        document.getElementById('previewTitle').innerText = `Vorschau: ${filename}`;
        const img = document.getElementById('pdfPreview');
        img.src = `${backend}/preview/${filename}?stamp=${encodeURIComponent(this.stampText)}`;
        img.style.display = 'block';
    }
}

// Modul-Einstiegspunkt
window.addEventListener('DOMContentLoaded', () => {
    new PdfStampApp();
});
