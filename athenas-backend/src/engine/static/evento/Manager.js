/**
 *
 **/
Ext._define('engine.evento.Manager', {
    'extend': 'toolkit.widget.TabPanel',

    'getGridPanel': function() {
        if(!this._gridPanel)
            this._gridPanel = Ext._create('engine.evento.RestfulGrid', {
                'border': false
            });

        return this._gridPanel;
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                'title': 'Eventos do Usuário'
            }
        );

        Ext.apply(
            cfg,
            {
                'items': [this.getGridPanel()],
                'layout': 'fit'
            }
        );

        // this.callParent([cfg]);
        engine.evento.Manager.superclass.constructor.call(this, cfg);
    }
})