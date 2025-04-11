Ext._define('media_indoor.config_campaign.Window', {
    extend: 'core.RestfulWindow',

    rest: 'media_indoor.config_campaign.Restful',

    width: 600,

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        name: "group",
                        fieldLabel: "Grupo",
                        xtype: "rest-autocompletefield",
                        allowBlank: false,
                        rest: "media_indoor.campaign_group.Restful",
                    },
                    {
                        name: "campaign",
                        fieldLabel: "Campanha",
                        xtype: "rest-autocompletefield",
                        allowBlank: false,
                        rest: "media_indoor.campaign.Restful",
                    },
                ]
            });

        return this._formPanel;
    },

});

