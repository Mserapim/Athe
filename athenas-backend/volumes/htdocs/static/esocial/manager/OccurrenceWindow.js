Ext._define("esocial.manager.OccurrenceWindow", {
    extend: "Ext.Window",

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.apply(cfg, {
            title: "Ocorrências",
            modal: false,
            width: 800,
            height: 700,
            border: false,
            scope: this,
            items: [this.getGridOccurrence(cfg), this.getDetailPanel(cfg)]
        });
        esocial.manager.OccurrenceWindow.superclass.constructor.call(this, cfg);
    },

    getGridOccurrence: function(cfg) {
        if (!this._grid) {
            this._grid = Ext._create("esocial.occurrence.Grid", {
                region: "center",
                gridAutoLoad: false,
                autoScroll: true,
                height: 370,
                hideActions: ["copy", "edit", "remove"],
                hideItemsToolbar: ["edit", "add", "remove"]
            });
            if (cfg.event_id != undefined) {
                this._grid.setFilterProperty("result__event__id", cfg.event_id);
            }
            if (cfg.batch_id != undefined) {
                this._grid.setFilterProperty("result__batch__id", cfg.batch_id);
            }


            this._grid.getSelectionModel().on({
                scope: this,
                rowselect: function (sm, index, data) {
                    this._updateDetail(data);
                },
            });

            var grid = this._grid;

            this._grid.getStore().on({
                scope: this,
                load: function(store, records, opts) {
                    grid.getSelectionModel().selectFirstRow();
                }
            });
        }
        return this._grid;
    },

    getDetailPanel: function(cfg) {
        if (!this._detailPanel) {
            this._detailPanel = Ext._create("Ext.Panel", {
                border: false,
                autoScroll: true,
                region: "south",
                height: 300,
                split: true,
            });
        }

        return this._detailPanel;
    },

    _updateDetail: function(data){
        data = core.nullValue(data, {});
        var tpl = new Ext.XTemplate("Carregando as informações do resumo...");
        if(data != undefined)
            tpl = new Ext.Template(
                '<div style="font-size:1.0em;padding-top:11px>"',
                '<p>Código:  {code}</p><br>',
                '<p>Tipo:  {type_occurrence}</p><br>',
                '<p>Descrição:  {description}</p><br>',
                '<p>Localização:  {location}</p><br>',
                '</div'
            );
        tpl.overwrite(this.getDetailPanel().body, data.data);
    }
});
