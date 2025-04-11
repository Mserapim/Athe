Ext._define("web.cms.file.Grid", {
    extend: "core.RestfulGrid",

    restWindow: "web.cms.file.Window",
    keywordFieldMessage: "Digite o termo para busca e tecle Enter",
    actionColumnWidth: 50,

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create("Ext.grid.ColumnModel", [
                { header: "Nome", dataIndex: "title", id: "autoExpandColumn" },
                { header: "Mês", dataIndex: "ref_month_name" },
                { header: "Criado em", dataIndex: "create_date" },
                { header: "Atualizado em", dataIndex: "user_date" },                
                { header: "Arquivo", dataIndex: "ged_unicode" },
            ]);

        return this._columnModel;
    },

    openApplyMonthWindow: function() {
        var selection = this.getSelectionModel().getSelections();

        if (selection.length > 0) {
            Ext._create('web.cms.file.ApplyMonthWindow', {
                pkset: selection.map(function(record) { return record.get('pk') }),
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            }).show();
        } else {
            Ext.Msg.show({
                title: 'Aplicando valor de mês',
                msg: 'Primeiro selecione os itens para aplicar o valor do mês.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OKONLY
            });
        }
    },

    getApplyMonthAction: function(cfg) {
        if (!this._applyMonthAction) {
            this._applyMonthAction = Ext._create('Ext.Button', {
                text: 'Aplicar valor de Mês',
                scope: this,
                handler: function () {
                    this.openApplyMonthWindow();
                }
            });
        }

        return this._applyMonthAction;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        web.cms.file.Grid.superclass.constructor.call(this, cfg);

        this.state = JSON.parse(sessionStorage.getItem("cms-state")) || {};

        var filter = [];

        if (this.state.post)
            filter.push({
                property: "posts",
                value: this.state.post,
                stage: 1,
            });

        this.setFilter(filter);
    },
});

core.RestfulGrid.register("web.cms.file.Restful", "web.cms.file.Grid");
