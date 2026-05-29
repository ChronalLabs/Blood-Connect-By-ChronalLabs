class CompatibilityMatrixWidget {
    constructor(root) {
        this.root = root;
        this.targetSelect = root.querySelector('#compatibility-target-type');
        this.modeRadios = Array.from(root.querySelectorAll('input[name="compatibility_mode"]'));
        this.summary = root.querySelector('#compatibility-summary');
        this.matrixBody = root.querySelector('#compatibility-matrix-body');
        this.resetButton = root.querySelector('#compatibility-reset');
        this.donorCards = Array.from(document.querySelectorAll('.donor-card'));
        this.compatibilityRules = this.getCompatibilityRules();
        this.bloodTypes = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'];
        this.init();
    }

    getCompatibilityRules() {
        return {
            rbc: new Map([
                ['A+', ['A+', 'A-', 'O+', 'O-']],
                ['A-', ['A-', 'O-']],
                ['B+', ['B+', 'B-', 'O+', 'O-']],
                ['B-', ['B-', 'O-']],
                ['AB+', ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']],
                ['AB-', ['A-', 'B-', 'AB-', 'O-']],
                ['O+', ['O+', 'O-']],
                ['O-', ['O-']],
            ]),
            plasma: new Map([
                ['A+', ['A+', 'A-', 'AB+', 'AB-']],
                ['A-', ['A-', 'AB-']],
                ['B+', ['B+', 'B-', 'AB+', 'AB-']],
                ['B-', ['B-', 'AB-']],
                ['AB+', ['AB+', 'AB-']],
                ['AB-', ['AB-']],
                ['O+', ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']],
                ['O-', ['O-', 'A-', 'B-', 'AB-']],
            ]),
        };
    }

    init() {
        if (!this.targetSelect || !this.summary) {
            return;
        }

        this.renderMatrix();
        this.attachEvents();
        this.updateCompatibility();
    }

    attachEvents() {
        this.targetSelect.addEventListener('change', () => this.updateCompatibility());
        this.modeRadios.forEach(radio => radio.addEventListener('change', () => this.updateCompatibility()));
        if (this.resetButton) {
            this.resetButton.addEventListener('click', (event) => {
                event.preventDefault();
                this.resetSelection();
            });
        }
    }

    getCurrentMode() {
        const selected = this.modeRadios.find(radio => radio.checked);
        return selected ? selected.value : 'rbc';
    }

    getCompatibleTypes(targetType, mode) {
        const modeMap = this.compatibilityRules[mode];
        if (!modeMap) {
            return [];
        }
        return modeMap.get(targetType) || [];
    }

    updateCompatibility() {
        window.requestAnimationFrame(() => {
            const targetType = this.targetSelect.value;
            const mode = this.getCurrentMode();
            const compatibleTypes = targetType ? this.getCompatibleTypes(targetType, mode) : [];
            const compatibilitySet = new Set(compatibleTypes);

            this.donorCards.forEach(card => {
                const donorType = card.dataset.donorBloodGroup?.trim() || '';
                card.classList.remove('compatible', 'incompatible');
                if (!targetType) {
                    return;
                }
                if (compatibilitySet.has(donorType)) {
                    card.classList.add('compatible');
                } else {
                    card.classList.add('incompatible');
                }
            });

            this.updateSummary(targetType, mode, compatibleTypes);
            this.updateMatrixCells(targetType, mode);
        });
    }

    updateSummary(targetType, mode, compatibleTypes) {
        if (!targetType) {
            this.summary.textContent = 'Select a target blood type to highlight compatible donors instantly.';
            return;
        }

        const universal = mode === 'rbc' && targetType === 'O-';
        const note = universal ? 'Universal donor for RBC recipients.' : '';
        this.summary.innerHTML = `
            <strong>${targetType}</strong> (${mode.toUpperCase()}) matches <strong>${compatibleTypes.length}</strong> donor type${compatibleTypes.length === 1 ? '' : 's'}.<br>
            ${compatibleTypes.join(', ')}${note ? `<br><em>${note}</em>` : ''}
        `;
    }

    renderMatrix() {
        if (!this.matrixBody) {
            return;
        }
        this.matrixBody.innerHTML = '';
        this.bloodTypes.forEach(donorType => {
            const row = document.createElement('tr');
            const labelCell = document.createElement('td');
            labelCell.textContent = donorType;
            row.appendChild(labelCell);
            this.bloodTypes.forEach(targetType => {
                const cell = document.createElement('td');
                cell.dataset.matrixTarget = targetType;
                cell.dataset.matrixDonor = donorType;
                cell.textContent = '--';
                row.appendChild(cell);
            });
            this.matrixBody.appendChild(row);
        });
    }

    updateMatrixCells(targetType, mode) {
        if (!this.matrixBody) {
            return;
        }

        const compatibleTypes = targetType ? this.getCompatibleTypes(targetType, mode) : [];
        const compatibilitySet = new Set(compatibleTypes);

        this.matrixBody.querySelectorAll('tr').forEach(row => {
            const donorType = row.children[0].textContent.trim();
            Array.from(row.children).slice(1).forEach(cell => {
                const target = cell.dataset.matrixTarget;
                if (!targetType || target !== targetType) {
                    cell.classList.remove('match', 'no-match');
                    cell.textContent = '--';
                    return;
                }
                const isMatch = compatibilitySet.has(donorType);
                cell.classList.toggle('match', isMatch);
                cell.classList.toggle('no-match', !isMatch);
                cell.textContent = isMatch ? '✓' : '✕';
            });
        });
    }

    resetSelection() {
        if (this.targetSelect) this.targetSelect.value = '';
        this.modeRadios.find(radio => radio.value === 'rbc').checked = true;
        this.updateCompatibility();
    }
}

window.addEventListener('DOMContentLoaded', () => {
    const widgetRoot = document.getElementById('compatibility-widget');
    if (widgetRoot) {
        new CompatibilityMatrixWidget(widgetRoot);
    }
});
