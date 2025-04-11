Ext._define("web.cms.post.ClassifyCategoryWindow", {
    extend: "Ext.Window",
    width: 720,

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create("Ext.form.FormPanel", {
                frame: true,
                items: [
                    {
                        name: "category",
                        fieldLabel: "Categoria",
                        xtype: "rest-autocompletefield",
                        rest: "web.cms.category.Restful",
                        emptyText: "Filtrar por categoria",
                        resizable: true,
                        // _FIXME_ fazer chegar a informação do site em questão
                        // preFilter: [
                        //     {
                        //         property: "posts__areas__parent__slug",
                        //         value: cfg.state.site,
                        //         stage: 1,
                        //     },
                        // ],
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
        rest.applyCategory(
            this.pkset,
            values.category,
            {
                scope: this,
                fn: function() {
                    core.invokeCallback((this.callback || {}).success || { fn: Ext.emptyFn });
                    this.close();
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: "Classificando",
                        msg: message,
                        buttons: Ext.Msg.OK,
                        icon: Ext.Msg.ERROR,
                    });
                }
            },
            {
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: "Classificar Categoria",
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

        web.cms.post.ClassifyCategoryWindow.superclass.constructor.call(this, cfg);
    },
});
