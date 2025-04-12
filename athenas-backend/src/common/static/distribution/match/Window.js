Ext._define('common.distribution.match.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.distribution.match.Restful',

    width: 500,

    getPlayerTitleField: function (cfg) {
        if (!this._playerTitleField) {
            this._playerTitleField = Ext._create('Ext.form.DisplayField', {
                fieldLabel: "Participante",
                style: {
                    fontWeight: 'bold',
                    marginBottom: '15px'
                },
                rest: "common.distribution.player.Restful",
                name: "player_title"
            });
        }
        return this._playerTitleField;
    },

    // Campo de choices para incident_type
    getIncidentTypeField: function (cfg) {
        if (!this._incidentTypeField) {
            this._incidentTypeField = Ext._create('Ext.form.ComboBox', {
                fieldLabel: "Tipo de Incidente",
                allowBlank: false,
                lazyRender: true,
                hiddenName: "incident_type",
                anchor: '99%',
                mode: "local",
                triggerAction: "all",
                store: [
                    [1, "Sem incidente"],
                    [2, "Conexão"],
                    [3, "Prevenção"],
                    [4, "Impedimento"],
                    [5, "Suspeição"]
                ],
                name: "incident_type"
            });
        }
        return this._incidentTypeField;
    },

    getIncidentDetailsField: function (cfg) {
        if (!this._incidentDetailsField) {
            this._incidentDetailsField = Ext._create('toolkit.fields.CKEditor', {
                allowBlank: true,
                name: "incident_details",
                editorConfig: {
                    toolbarStartupExpanded: false
                },
                submitValue: true,
                //startupFocus: false
            });
        }
        return this._incidentDetailsField;
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 100,
                labelAlign: 'right',
                items: [
                    this.getPlayerTitleField(cfg),
                    this.getIncidentTypeField(cfg),
                    {
                        xtype: 'panel',
                        title: 'Detalhes do incidente (opcional)',
                        style: {marginTop: '15px'},
                        items: this.getIncidentDetailsField(cfg)
                    }
                ]
            });
        }
        return this._formPanel;
    }
});
