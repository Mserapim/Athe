Ext._define('edocs.protocolo.requestform.resignation.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormResignation',

    rest: 'edocs.protocolo.requestform.resignation.Restful',

    width: 900,

    getStartDateField: function (cfg) {
        if (!this._startDateField) {
            this._startDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: "Data de início",
                emptyText: 'Início da exoneração...',
                name: "start_date",
                width: 210,
                allowBlank: false
            });
        }

        return this._startDateField;
    },

    getActivePossessionsField: function (cfg) {
        if (!this._activePossessionsField) {
            this._activePossessionsField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Cargo',
                hiddenName: 'possession',
                valueField: 'pk',
                displayField: 'description',
                anchor: '99%',
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction(this._resource, 'active_possessions')
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            { name: 'pk', type: 'int' },
                            { name: 'description', type: 'string' }
                        ]
                    }),
                }),
                allowBlank: false
            });
        }

        return this._activePossessionsField;
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
                                items: this.getDocumentTypeField('REQUERIMENTO')  // mixin
                            }
                        ]
                    },
                    this.getSubjectField(cfg, {
                        value: 'Requerimento de Exoneração',
                        readOnly: true,
                    }),
                    this.getControlContainer(cfg),
                    this.getActivePossessionsField(cfg),
                    this.getStartDateField(cfg)
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
                items: this.getMainPanel(cfg)
            });
        }

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento de Exoneração',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.resignation.Window',
    specialType: 'resignation',
    group: 'Vacância e exoneração'
});
