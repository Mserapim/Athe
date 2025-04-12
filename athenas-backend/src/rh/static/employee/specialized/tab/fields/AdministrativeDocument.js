
rh.employee.specialized.tab.fields.AdministrativeDocument = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function(cfg) {
            rh.employee.specialized.tab.fields.AdministrativeDocument.superclass.constructor.call(this, cfg);
        },

        observerNaturalPersonPk: function(){
            rh.employee.specialized.tab.fields.AdministrativeDocument.superclass.observerNaturalPersonPk.call(this, {});
            if(this.myParams('employeePk')){
                this.getDigitalDocumentGrid().enable();
                this.getDigitalDocumentGrid().setParam('employee', this.myParams('employeePk'));
                this.getDigitalDocumentGrid().setFilterProperty('employee__id', this.myParams('employeePk'), 100, false);
                this.getDigitalDocumentGrid().setFilterProperty('document_type__in', [57, ], 101);
            }else{
                this.getDigitalDocumentGrid().setParam('employee', undefined);
                this.getDigitalDocumentGrid().removeFilterProperty('employee__id', 100, false);
                this.getDigitalDocumentGrid().removeFilterProperty('document_type__in', 101, false);
                this.getDigitalDocumentGrid().disable();
            }
        },

        fields: function(cfg){
            return [
                this.getDigitalDocumentGrid({}),
            ];
        },

        getDigitalDocumentGrid: function(cfg) {
            if(!this._documentGrid) {
                this._documentGrid = Ext._create('rh.digitaldocument.attachment.Grid', {
                    region: 'center',
                    hideItemsToolbar: ['search', 'download'],
                    border: false,
                    height: 430,
                    gridAutoLoad: false,
                    hideColumns: [
                        'date_start',
                        'date_end',
                    ]
                });
                this._documentGrid.on({
                    scope: this,
                    createdItemGrid: function(instance) {
                        this.updateEmployeePanel();
                    },
                    updatedItemGrid: function(instance) {
                        this.updateEmployeePanel();
                    },
                    removedItemGrid: function(instance) {
                        this.updateEmployeePanel();
                    }
                });
            }
            return this._documentGrid;
        },
    }
);
