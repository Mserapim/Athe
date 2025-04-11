Ext._define('edocs.protocolo.requestform.vacationdaysell.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormVacationDaySell',

    rest: 'edocs.protocolo.requestform.vacationdaysell.Restful',

    width: 900,

    getDaysField: function (cfg) {
        if (!this._daysField) {
            this._daysField = Ext._create('Ext.form.NumberField', {
                fieldLabel: "Dias",
                name: "days",
                width: 200,
                maxLength: 7
            });
        }

        return this._daysField;
    },

    getVacationPeriodsGrid: function (cfg) {
        if (!this._vacationPeriodsGrid) {
            this._vacationPeriodsGrid = Ext._create('edocs.protocolo.requestform.vacationdaysell.EmployeeAcquisitionPeriodGrid', {
                rest: 'edocs.protocolo.requestform.vacationdaysell.EmployeeAcquisitionPeriodRestful',
                title: 'Períodos de Férias - Apenas para conferência',
                hideItemsToolbar: ['add', 'edit', 'remove', 'search', 'download'],
                hideActions: ['add', 'edit', 'remove', 'copy'],
                height: 300
            });
        }
        return this._vacationPeriodsGrid;
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: true,
                layout: 'form',
                items: [
                    this.getCodeField(cfg),
                    {
                        xtype: 'container',
                        layout: 'hbox',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 2.75,
                                items: this.getHomeCourtField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.25,
                                labelWidth: 50,
                                items: this.getDocumentTypeField('INDENIZAÇÃO DE FÉRIAS')  // mixin
                            }
                        ]
                    },
                    this.getSubjectField(cfg, {
                        value: 'Requerimento de indenização de férias adquiridas e não usufruidas',
                        readOnly: true,
                    }),
                    this.getControlContainer(cfg),
                    this.getDaysField(cfg),
                ]
            });
        }

        return this._mainPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                height: 'auto',
                autoHeight: true,
                items: [
                    this.getMainPanel(cfg),
                    this.getVacationPeriodsGrid(cfg)
                ]
            });
        }

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento de Indenização de Férias',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.vacationdaysell.Window',
    specialType: 'vacationdaysell',
    group: 'Auxílios, indenizações, vales e valores a receber e a antecipar'
});
