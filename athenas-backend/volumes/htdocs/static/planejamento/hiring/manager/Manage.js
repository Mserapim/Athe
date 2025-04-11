Ext._define('planning.hiring.manager.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getManageGrid: function() {
        if(!this._manage) {
            this._manage = Ext._create('planning.hiring.manager.Grid', {
                region: 'center'
            });
        }

        return this._manage;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});[]

        Ext.applyIf(
            cfg,
            {
                title: 'Permissões de Gerência de Contratos'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getManageGrid(),
                ]
            }
        );

        planning.hiring.manager.Manage.superclass.constructor.call(this, cfg);
    }
});
