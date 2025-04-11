Ext._define('esocial.manager.DependencyWindow', {
    extend: 'Ext.Window',

    constructor: function (cfg) {

        cfg = (cfg ? cfg : {});

        Ext.apply(cfg, {
            title: "Dependências",
            modal: false,
            width: 850,
            height: 700,
            border: false,
            scope: this,
            items: this.getDependencyGrid(cfg),
        });
        esocial.manager.DependencyWindow.superclass.constructor.call(this, cfg);
    },

    getDependencyGrid: function (cfg) {
        if (!this._dependencyGrid) {
            this._dependencyGrid = Ext._create("esocial.dependency.DependencyGrid", {
                region: "center",
                gridAutoLoad: false,
                autoScroll: true,
                // width: 790,
                height: 670,
                hideItemsToolbar: ["add", "edit", "remove", "-", "search", "->", "download"],
                hideActions: ["copy", "edit", "remove"],
            });

            if (cfg.event_id != undefined) {
                this._dependencyGrid.setFilterProperty('event__id', cfg.event_id);
            }
        }
        return this._dependencyGrid;
    },
});
