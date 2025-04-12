Ext._define("web.cms.post.Manager", {
    extend: "toolkit.widget.TabPanel",

    getGrid: function () {
        if (!this._grid) {
            this._grid = Ext._create("web.cms.post.Grid", {
                region: "center",
                gridAutoLoad: false,
                state: this.state,
            });

            this._grid.setFilter([
                {
                    property: "areas__parent__slug",
                    value: this.state.site,
                    stage: 1,
                },
            ]);

            this._grid.getSelectionModel().on({
                scope: this,
                selectionchange: function (sm) {
                    var selection = sm.getSelections();

                    if (selection.length > 0) {
                        this.post(selection[0].get("pk"));
                    } else {
                        this.post(null);
                    }
                },
            });
        }

        return this._grid;
    },

    post: function (value, dispatch) {
        dispatch = dispatch === undefined ? true : dispatch;

        if (value) {
            this._post = value;

            if (dispatch) {
                this.observePost();
            }
        }

        return this._post;
    },

    observePost: function () {
        var value = this.post();

        if (value) {
            this.getFilePanel().enable();
            this.getFilePanel().setParam('posts', [value]);
            this.getFilePanel().setFilterProperty('posts', value, 100);
        } else {
            this.getFilePanel().disable();
            this.getFilePanel().setFilterProperty("posts", 0, 100, false);
            this.getFilePanel().getStore().removeAll();
        }
    },

    getFilePanel: function (cfg) {
        if (!this._filePanel) {
            this._filePanel = Ext._create("web.cms.file.Grid", {
                title: "Anexos",
                region: "south",
                minHeight: 320,
                height: 320,
                split: true,
                configOrderToolBar: ["-", "applyMonth", "-", "search", "->", "-"],
                gridAutoLoad: false,
            });
        }

        return this._filePanel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        this.state = cfg.initialState || {};

        var site = sessionStorage.getItem("site");
        if (site) this.state.site_pk = site;

        sessionStorage.setItem("cms-state", JSON.stringify(this.state));

        Ext.applyIf(cfg, {
            title: "Gestor de Publicações",
            layout: "border",
            items: [this.getGrid(cfg), this.getFilePanel(cfg)],
        });

        web.cms.post.Manager.superclass.constructor.call(this, cfg);
        this.observePost();
    },
});
