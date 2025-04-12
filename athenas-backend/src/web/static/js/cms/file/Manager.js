Ext._define('web.cms.file.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function () {
        if (!this._grid) {
            this._grid = Ext._create('web.cms.file.Grid', {
                region: 'center',
                gridAutoLoad: false,
            });           
        }

        return this._grid;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        this.state = JSON.parse(sessionStorage.getItem('cms-state')) || {};

        Ext.applyIf(cfg, {
            title: 'Gestor de Arquivos para Download',
            layout: 'border',
            items: [this.getGrid()],
        });

        web.cms.file.Manager.superclass.constructor.call(this, cfg);
    },
});
