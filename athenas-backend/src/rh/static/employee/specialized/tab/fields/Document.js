
rh.employee.specialized.tab.fields.Document = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function (cfg) {
            rh.employee.specialized.tab.fields.Document.superclass.constructor.call(this, cfg);
        },

        observerNaturalPersonPk: function () {
            rh.employee.specialized.tab.fields.Document.superclass.observerNaturalPersonPk.call(this, {});
            if (this.myParams('naturalPersonPk')) {
                this.getDocumentGrid().enable();
                this.getDocumentGrid().setParam('naturalpersons', this.myParams('naturalPersonPk'));
                this.getDocumentGrid().setParam('natural_person', this.myParams('naturalPersonPk'));
                this.getDocumentGrid().setFilterProperty('naturalpersons__id', this.myParams('naturalPersonPk'), 100, false);
                this.getDocumentGrid().setFilterProperty('natural_person__id', this.myParams('naturalPersonPk'), 100);
            } else {
                this.getDocumentGrid().setParam('natural_person', undefined);
                this.getDocumentGrid().setParam('naturalpersons', undefined);
                this.getDocumentGrid().setFilterProperty('naturalpersons__id', 0, 100, false);
                this.getDocumentGrid().setFilterProperty('natural_person__id', 0, 100);
                this.getDocumentGrid().disable();
            }
            this.observerDocumentPk(null, null);
        },

        observerDocumentPk: function (pk, documentType) {
            var employeePk = this.myParams('employeePk');
            if (documentType != undefined)
                this.getDigitalDocumentGrid().setParam('document_type', documentType);

            if (pk != undefined) {
                this.getDigitalDocumentGrid().setParam('document_natural_person', pk);
                this.getDigitalDocumentGrid().setFilterProperty('document_natural_person__id', pk, 100, false);
            } else {
                this.getDigitalDocumentGrid().setParam('document_natural_person', undefined);
                this.getDigitalDocumentGrid().setFilterProperty('document_natural_person__id', 0, 100, false);
                this.getDigitalDocumentGrid().disable();
            }

            if (employeePk != undefined) {
                this.getDigitalDocumentGrid().enable();
                this.getDigitalDocumentGrid().setParam('employee', employeePk);
                this.getDigitalDocumentGrid().setFilterProperty('employee__id', employeePk, 200);
            } else {
                this.getDigitalDocumentGrid().disable();
                this.getDigitalDocumentGrid().setParam('employee', undefined);
                this.getDigitalDocumentGrid().setFilterProperty('employee__id', 0, 200);
            }
        },

        fields: function (cfg) {
            return [
                this.getDocumentGrid({}),
                this.getDigitalDocumentGrid({}),
            ];
        },

        getDocumentGrid: function (cfg) {
            if (!this._documentGrid) {
                this._documentGrid = Ext._create('rh.documento.DocumentoGrid', {
                    region: 'center',
                    hideItemsToolbar: ['search', 'download'],
                    border: false,
                    height: 330,
                    gridAutoLoad: false,
                    canEditCpfRg: false,
                    messageToUser: 'Utilize os campos da aba Dados Funcionais'
                });
                this._documentGrid.on({
                    scope: this,
                    createdItemGrid: function (instance) {
                        this.updateEmployeePanel();
                    },
                    updatedItemGrid: function (instance) {
                        this.updateEmployeePanel();
                    },
                    removedItemGrid: function (instance) {
                        this.updateEmployeePanel();
                    }
                });
                this._documentGrid.getSelectionModel().on({
                    scope: this,
                    rowselect: function (sm, index, record) {
                        this.observerDocumentPk(record.get('pk'), record.get('tipo_documento'));
                    },
                    rowdeselect: function (sm) {
                        this.observerDocumentPk(null, null);
                    }
                });
            }
            return this._documentGrid;
        },

        getDigitalDocumentGrid: function (cfg) {
            if (!this._digitalDocumentGrid) {
                this._digitalDocumentGrid = Ext._create('rh.digitaldocument.naturalperson.Grid', {
                    title: 'Arquivos',
                    region: 'center',
                    hideItemsToolbar: ['search', 'download'],
                    border: false,
                    height: 230,
                    gridAutoLoad: false,
                });
                this._digitalDocumentGrid.on({
                    scope: this,
                    createdItemGrid: function (instance) {
                        this.updateEmployeePanel();
                    },
                    updatedItemGrid: function (instance) {
                        this.updateEmployeePanel();
                    },
                    removedItemGrid: function (instance) {
                        this.updateEmployeePanel();
                    },
                });
            }
            return this._digitalDocumentGrid;
        },
    }
);
