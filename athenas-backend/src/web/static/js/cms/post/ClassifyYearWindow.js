Ext._define("web.cms.post.ClassifyYearWindow", {
    extend: "Ext.Window",
    width: 320,

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create("Ext.form.FormPanel", {
                frame: true,
                items: [
                    {
                        xtype: "numberfield",
                        name: "ref_year",
                        fieldLabel: "Ano de Ref.",
                        value: cfg.value || "",
                    },
                ],
            });
        }

        return this._formPanel;
    },

    save: function () {
        var values = this.getFormPanel().getForm().getValues();
        var rest = Ext._create("web.cms.post.Restful");
        var mask = new Ext.LoadMask(this.getEl(), { msg: "Persistindo dados ..." });

        values.filter = Ext.encode([
            {
                property: "pk__in",
                value: this.pkset,
                stage: 1,
            },
        ]);

        mask.show();
        rest.doRequest(
            rest.getRoute("update", null, "PUT", {
                params: values,
                scope: this,
                callback: function () {},
                success: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if (rst.success) {
                        core.invokeCallback((this.callback || {}).success || { fn: Ext.emptyFn });
                        this.close();
                    } else {
                        Ext.Msg.show({
                            title: "Classificando",
                            msg: rst.message,
                            btn: Ext.Msg.OKONLY,
                            icon: Ext.Msg.ERROR,
                        });
                    }
                },
                failure: function () {
                    Ext.Msg.show({
                        title: "Classificando",
                        msg: "Recurso indisponível no momento.",
                        btn: Ext.Msg.OKONLY,
                        icon: Ext.Msg.ERROR,
                    });
                },
                callback: {
                    fn: function () {
                        mask.hide();
                    },
                },
            })
        );
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: "Classificar ano",
            closable: true,
            modal: true,
            items: [this.getFormPanel(cfg)],
            buttons: [
                {
                    text: "Aplicar",
                    scope: this,
                    handler: function () {
                        this.save();
                    },
                },
                {
                    text: "Cancelar",
                    scope: this,
                    handler: function () {
                        this.close();
                    },
                },
            ],
        });

        web.cms.post.ClassifyYearWindow.superclass.constructor.call(this, cfg);
    },
});
