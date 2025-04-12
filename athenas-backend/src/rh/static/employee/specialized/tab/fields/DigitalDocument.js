
rh.employee.specialized.tab.fields.DigitalDocument = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function (cfg) {
            rh.employee.specialized.tab.fields.DigitalDocument.superclass.constructor.call(this, cfg);
        },

        observerNaturalPersonPk: function () {
            rh.employee.specialized.tab.fields.DigitalDocument.superclass.observerNaturalPersonPk.call(this, {});
            if (this.myParams('naturalPersonPk')) {
                this.getDigitalDocumentGrid().setFilterProperty('person__id', this.myParams('naturalPersonPk'), 100, false);
            } else {
                this.getDigitalDocumentGrid().setFilterProperty('person__id', 0, 100, false);
            }
            if (this.myParams('employeePk')) {
                this.getDigitalDocumentGrid().enable();
                this.getDigitalDocumentGrid().setParam('employee', this.myParams('employeePk'));
                this.getDigitalDocumentGrid().setParam(
                    'exclude_document_type',
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
                );
                this.getDigitalDocumentGrid().setFilterProperty('employee__id', this.myParams('employeePk'), 100);
            } else {
                this.getDigitalDocumentGrid().setParam('employee', undefined);
                this.getDigitalDocumentGrid().setFilterProperty('employee__id', 0, 100);
                this.getDigitalDocumentGrid().disable();
            }
        },

        fields: function (cfg) {
            return [
                this.getDigitalDocumentGrid({}),
            ];
        },

        getDigitalDocumentGrid: function (cfg) {
            if (!this._documentGrid) {
                this._documentGrid = Ext._create('rh.digitaldocument.Grid', {
                    region: 'center',
                    hideItemsToolbar: ['search', 'download'],
                    border: false,
                    height: 430,
                    gridAutoLoad: false
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
            }
            return this._documentGrid;
        },
    }
);
