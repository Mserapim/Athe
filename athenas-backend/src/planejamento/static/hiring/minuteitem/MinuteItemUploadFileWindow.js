Ext._define('planning.hiring.minuteitem.MinuteItemUploadFileWindow', {
    extend: 'Ext.Window',

    uploadForm: function () {
        if (!this._uploadForm) {
            this._uploadForm = Ext._create('Ext.form.FormPanel', {
                style: "margin: 5pt",
                border: false,
                labelWidth: 60,
                fileUpload: true,
                defaults: {
                    width: 250
                },
                items: [
                    {
                        name: "file",
                        xtype: "fileuploadfield",
                        fieldLabel: "Arquivo",
                        buttonCfg: {
                            iconCls: true,
                            icon: "/" + global.Context + "/static/images/upload.png",
                            text: ""
                        },
                    },
                ]
            });
        }

        return this._uploadForm;
    },

    uploadFile: function () {
        var form = this.uploadForm().getForm();

        try {
            form.submit({
                url: toolkit.util.Normalize.controller_action('PHMMinuteItem', 'import_items'),
                params: { minute: this.params.minute },
                waitMsg: "Enviando arquivo para o servidor...",
                scope: this,
                success: function (form, action) {
                    this.success && this.success.callback.call(this.success.scope ? this.success.scope : window);
                    if (close) this.destroy();
                    Ext.Msg.show({
                        title: 'Importação de Itens',
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK,
                        msg: action.result.message
                    });

                    Ext._create('planning.hiring.minuteitem.MinuteItemWindowValidator', {
                        title: 'Itens para validação',
                        params: this.params,
                        gridItems: this.gridItems
                    }).show();
                },
                failure: function (form, action) {
                    Ext.Msg.show({
                        title: 'Importação de Itens',
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK,
                        msg: action.result.message
                    });
                },
            });
        } catch (e) {
            console.debug(e);
        }


    },

    constructor: function (cfg) {
        cfg = cfg || {};

        this.form = this.uploadForm();

        Ext.applyIf(cfg, {
            title: "Anexar arquivo",
            closable: true,
            modal: true,
            items: new Ext.Panel({
                border: false,
                items: this.form
            }),
            width: 400,
            buttons: [
                {
                    text: "Anexar",
                    handler: this.uploadFile,
                    scope: this
                },
                {
                    text: "Cancelar",
                    scope: this,
                    handler: function () {
                        this.destroy();
                    }
                }
            ]

        });

        planning.hiring.minuteitem.MinuteItemUploadFileWindow.superclass.constructor.call(this, cfg);

    }
});
