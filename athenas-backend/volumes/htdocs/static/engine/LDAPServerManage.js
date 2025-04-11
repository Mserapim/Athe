/**
 *
 **/
Ext._define('engine.LDAPServerManage', {
    extend: 'toolkit.widget.TabPanel',

    getGridPanel: function() {
        if(!this._gridPanel)
            this._gridPanel = Ext._create('engine.LDAPServerGrid');

        return this._gridPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Configurações do LDAP'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'fit',
                items: [
                    this.getGridPanel()
                ]
            }
        );

        // this.callParent([cfg]);
        engine.LDAPServerManage.superclass.constructor.call(this, cfg);
    }
});
