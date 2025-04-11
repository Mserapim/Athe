/**
 *
 **/
Ext._define("rh.movimentacao.possession.request.Restful", {
    extend: "rh.movimentacao.possession.Restful",

    resource: "RHRequestMove",

    getFields: function () {
        return rh.movimentacao.possession.request.Restful.superclass.getFields.call(this).concat([
            { name: "pk", type: "string" },
            { name: "organ_origin_unicode", type: "string" },
            { name: "organ_origin", type: "int" },
            { name: "possession_origin_unicode", type: "string" },
            { name: "possession_origin", type: "int" },
            { name: "onus_display", type: "string" },
            { name: "onus", type: "int" },
            { name: "category", type: "int", useNull: true },
            { name: "category_display", type: "string" },
            { type: "date", name: "possession_origin_date", dateFormat: "d/m/Y" },
            { name: "job_position_origin", type: "string" },
            { type: "int", name: "cbo", useNull: true },
            { type: "string", name: "cbo_unicode" },
        ]);
    },
});
