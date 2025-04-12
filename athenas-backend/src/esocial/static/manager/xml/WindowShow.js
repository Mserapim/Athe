Ext._define("esocial.manager.xml.WindowShow", {
    extend: "Ext.Window",
    // extend: 'toolkit.widget.TabPanel',

    codeEditorCustomConfig: {
        editorConf: {
            mode: 'application/xml',
            lineWrapping: true,
            readOnly: true,
        },
        width: "100%",
        height: "100%",
    },

    getXMLContent: function (cfg) {
        if (!this._editorXml) {
            this._editorXml = Ext._create(
                "core.fields.CodeEditor",
                Ext.apply(this.codeEditorCustomConfig, {
                    value: cfg.xmlContent,
                })
            );
        }

        return this._editorXml;
    },

    getXMLContentPanel: function (cfg) {
        if (!this._editorXmlPanel) {
            this._editorXmlPanel = Ext._create("Ext.Panel", {
                title: "Conteúdo - XML",
                flex: 1,
                border: false,
                items: [this.getXMLContent(cfg)],
            });
        }

        return this._editorXmlPanel;
    },

    getXMLReceipt: function (cfg) {
        if (!this._editorXmlReceipt) {
            this._editorXmlReceipt = Ext._create(
                "core.fields.CodeEditor",
                Ext.apply(this.codeEditorCustomConfig, {
                    value: cfg.xmlReceipt,
                })
            );
        }

        return this._editorXmlReceipt;
    },

    getXMLReceiptPanel: function (cfg) {
        if (!this._editorXmlReceiptPanel) {
            this._editorXmlReceiptPanel = Ext._create("Ext.Panel", {
                title: "Retorno do envio",
                flex: 1,
                border: false,
                disabled: cfg.xmlReceipt == "" ? true : false,
                items: [this.getXMLReceipt(cfg)],
            });
        }

        return this._editorXmlReceiptPanel;
    },

    getXMLProcess: function (cfg) {
        if (!this._editorXmlProcess) {
            this._editorXmlProcess = Ext._create(
                "core.fields.CodeEditor",
                Ext.apply(this.codeEditorCustomConfig, {
                    value: cfg.xmlProcess,
                })
            );
        }

        return this._editorXmlProcess;
    },

    getXMLDiff: function (cfg) {
        if (!this._editorXmlDiff) {
            this._editorXmlDiff = Ext._create(
                "core.fields.CodeEditor",
                Ext.apply(this.codeEditorCustomConfig, {
                    value: cfg.xmlDiff,
                })
            );
        }
        return this._editorXmlDiff;
    },

    getXMLProcessPanel: function (cfg) {
        if (!this._editorXmlProcessPanel) {
            this._editorXmlProcessPanel = Ext._create("Ext.Panel", {
                title: "Retorno do processamento",
                flex: 1,
                border: false,
                disabled: cfg.xmlProcess == "" ? true : false,
                items: [this.getXMLProcess(cfg)],
            });
        }

        return this._editorXmlProcessPanel;
    },

    getXMLDiffContentPanel: function (cfg) {
        if (!this._editorXmlDiffPanel) {
            this._editorXmlDiffPanel = Ext._create("Ext.Panel", {
                title: "Diferença - XML",
                flex: 1,
                border: false,
                items: [this.getXMLDiff(cfg)],
            });
        }

        return this._editorXmlDiffPanel;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: "Visualização do XML - Envio, processado e retorno.",
        });

        Ext.apply(cfg, {
            width: 800,
            height: 850,
            scope: this,
            autoScroll: true,
            layout: {
                type: "hbox",
                align: "stretch",
            },
            border: false,
            items: [
                {
                    xtype: "tabpanel",
                    height: 700,
                    activeItem: 0,
                    items: [
                        this.getXMLContentPanel(cfg),
                        this.getXMLReceiptPanel(cfg),
                        this.getXMLProcessPanel(cfg),
                        this.getXMLDiffContentPanel(cfg),
                        // this.getTabForm()
                    ],
                },
            ],
            // html: '<div id="xmlContainer'+cfg.identifier+'" style="font-size:14px"></div>',
            // listeners: {
            //     afterrender: function() {
            //         var xmlContainer = Ext.get('xmlContainer'+cfg.identifier);
            //         xmlContainer.update('<pre>' + Ext.util.Format.htmlEncode(cfg.xml_value) + '</pre>');
            //     }
            // }
        });
        esocial.manager.xml.WindowShow.superclass.constructor.call(this, cfg);
    },
});
