/**
 *
 **/
Ext._define('estagio.comissaoavaliacao.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getComissaoServidorGrid: function() {
        if(!this._comissaoGrid) {
            this._comissaoGrid = Ext._create('estagio.comissaoavaliacao.EstagioComissaoServidorGrid', {
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
                title: 'Apreciação de Estágio Probatório'
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

        estagio.comissaoavaliacao.Manage.superclass.constructor.call(this, cfg);
    }
});
