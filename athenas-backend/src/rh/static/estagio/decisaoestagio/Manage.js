/**
 *
 **/
Ext._define('estagio.decisaoestagio.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getComissaoServidorGrid: function() {
        if(!this._comissaoGrid) {
            this._comissaoGrid = Ext._create('estagio.decisaoestagio.DecisaoEstagioGrid', {
                region: 'center',
            });
        }

        return this._comissaoGrid;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Decisão de Estágio Probatório'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getComissaoServidorGrid(),
                ]
            }
        );

        estagio.decisaoestagio.Manage.superclass.constructor.call(this, cfg);
    }
});
