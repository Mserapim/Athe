/**
 *
 **/
Ext._define("rh.movimentacao.possession.request.Grid", {
    extend: "rh.movimentacao.possession.Grid",

    restWindow: "rh.movimentacao.possession.request.Window",

    singleton: {
        types: [],
    },

    constructor: function (cfg) {
        rh.movimentacao.possession.request.Grid.superclass.constructor.call(this, cfg);
    },

    getColumnModelItems: function () {
        if (!this._columnModelItems) {
            this._columnModelItems = rh.movimentacao.possession.request.Grid.superclass.getColumnModelItems.call(this, {});
            console.info(this._columnModelItems);
            this._columnModelItems = this.itemRemove(this._columnModelItems, "bond");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "public_concurrence_unicode");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "data_posse");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "data_exercicio");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "data_desligamento");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "desligamento_unicode");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "jobposition_law_display");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "tipo_movcarreira_display");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "description_possession");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "quadro_unicode");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "unicode");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "ativo");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "servidor_unicode");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "anota");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "publicacao_movimentacao_unicode");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "publicacao_alteracao_unicode");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "texto");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "created_by_unicode");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "created_at");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "modified_by_unicode");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "modified_at");
            this._columnModelItems = this.itemRemove(this._columnModelItems, "anotacao_geral_unicode");
            this._columnModelItems = this._columnModelItems.concat([
                {
                    header: "Ativo",
                    dataIndex: "ativo",
                    width: 50,
                    renderer: toolkit.util.formatIconYesNo,
                },
                { header: "Servidor", dataIndex: "servidor_unicode", id: "autoExpandColumn", hidden: false },
                { header: "Origem", dataIndex: "organ_origin_unicode" },
                { header: "Ônus", dataIndex: "onus_display" },
                { header: "Categoria Origem(esocial)", dataIndex: "category_display" },
                {
                    header: "Início origem",
                    dataIndex: "possession_origin_date",
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y"),
                },
                {header: 'Cbo', dataIndex: 'cbo_unicode', width: 120, hidden: true},
                { header: "Cargo Origem", dataIndex: "job_position_origin" },
                { header: "Publicação", dataIndex: "publicacao_movimentacao_unicode", width: 150, hidden: false },
                {
                    header: "Início",
                    dataIndex: "data_exercicio",
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y"),
                },
                {
                    header: "Fim",
                    dataIndex: "data_desligamento",
                    width: 110,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y"),
                },
                { header: "Pub. Desligamento", dataIndex: "fired_publication_unicode", width: 120, hidden: true },
                { header: "Publicação Alteração", dataIndex: "publicacao_alteracao_unicode", width: 120, hidden: true },
                {
                    header: "Gera Anotação",
                    dataIndex: "anota",
                    width: 90,
                    renderer: function (value) {
                        return value ? "SIM" : "NÃO";
                    },
                    hidden: true,
                },
                { header: "Criado por", dataIndex: "created_by_unicode", hidden: true, width: 120, hidden: true },
                {
                    header: "Criado em",
                    dataIndex: "created_at",
                    hidden: true,
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y H:i"),
                    hidden: true,
                },
                { header: "Modificado por", dataIndex: "modified_by_unicode", hidden: true, width: 120, hidden: true },
                {
                    header: "Modificado em",
                    dataIndex: "modified_at",
                    hidden: true,
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y H:i"),
                    hidden: true,
                },
            ]);
        }
        return this._columnModelItems;
    },

    // getColumnModel: function () {
    //     if (!this._columnModel)
    //         this._columnModel = Ext._create("Ext.grid.ColumnModel", [
    //             Ext._create("Ext.grid.RowNumberer"),
    //             { header: "Cod.", dataIndex: "pk", width: 50 },
    //             { header: "Servidor", dataIndex: "servidor_unicode", id: "autoExpandColumn" },
    //             { header: "Origem", dataIndex: "organ_origin_unicode" },
    //             { header: "Data início", dataIndex: "data_exercicio", width: 95 },
    //             { header: "Data fim", dataIndex: "data_desligamento", width: 95 },
    //             { header: "Publicação", dataIndex: "publicacao_movimentacao_unicode" },
    //             { header: "Ônus", dataIndex: "onus_display" },
    //             { header: "Categoria Origem(esocial)", dataIndex: "category_display" },
    //             { header: "Pub. Alteração", dataIndex: "publicacao_alteracao_unicode", hidden: true },
    //             {
    //                 header: "Anota",
    //                 dataIndex: "anota",
    //                 renderer: function (v) {
    //                     return v ? "Sim" : "Não";
    //                 },
    //                 width: 60,
    //                 hidden: true,
    //             },
    //         ]);

    //     return this._columnModel;
    // },
});

core.RestfulGrid.register(
    'rh.movimentacao.possession.request.Restful',
    'rh.movimentacao.possession.request.Grid'
);
