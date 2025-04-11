Ext._define('judicial.taxonomy.LegalClassWindow', {
    extend: 'judicial.taxonomy.LegalClassificationWindow',

    rest: 'judicial.taxonomy.LegalClassRestful',

    getConfigurationPanel: function(cfg) {
        if(!this._configurationPanel)
            this._configurationPanel = Ext._create('Ext.Panel', {
                title: 'Configurações',
                layout: 'form',
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Instauração',
                        hiddenName: 'instauration',
                        choiceId: 'judicial.CLASS_INSTAURATION',
                        withNone: true,
                        withNoneLabel: 'Não pode ser instaurado'
                    }
                ]
            });

        return this._configurationPanel;
    },

    _allTabs: function(cfg) {
        return judicial.taxonomy.LegalClassWindow.superclass._allTabs.call(this, cfg).concat([
            this.getConfigurationPanel(cfg)
        ]);
    }
});
