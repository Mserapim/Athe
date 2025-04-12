Ext._define('media_indoor.config_campaign.Restful', {
    extend: 'core.Restful',

    resource: 'MIConfigCampaignGroup',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = media_indoor.config_campaign.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    name: "created_by",
                    type: "int",
                    useNull: true
                },
                {
                    name: "created_by_unicode",
                    type: "string"
                },
                {
                    name: "modified_by",
                    type: "int",
                    useNull: true
                },
                {
                    name: "modified_by_unicode",
                    type: "string"
                },
                {
                    name: "created_at",
                    type: "date",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    name: "modified_at",
                    type: "date",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    name: "group",
                    type: "int"
                },
                {
                    name: "group_unicode",
                    type: "string"
                },
                {
                    name: "campaign",
                    type: "int"
                },
                {
                    name: "campaign_unicode",
                    type: "string"
                },
            ]);

        return this._fields;
    }
});
