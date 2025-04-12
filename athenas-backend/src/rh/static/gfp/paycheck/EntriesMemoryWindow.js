Ext._define("rh.gfp.paycheck.EntriesMemoryWindow", {
    extend: "Ext.Window",
    // extend: 'toolkit.widget.TabPanel',

    codeEditorCustomConfig: {
        editorConf: {
            mode: 'markdown',
            lineWrapping: true,
            readOnly: true,
        },
        width: "100%",
        height: "100%",
    },

    getContentFromArray: function (memory, line = '') {
        console.info("INIT " + line);
        var content = {};
        var line_level = 1;
        if (!content[line]) {
            content[line] = '';
            console.info(" Start OBJ " + line);
        }
        memory.forEach(el_array => {
            var preLabel = (line == '' ? line_level : line + '.' + line_level)
            console.info(" Line for " + preLabel + " " + el_array[1].length + " > " + el_array[0]);
            content[line] += preLabel + ' ' + el_array[0] + '\n';
            if (Array.isArray(el_array[1]) && el_array[1].length > 0) {
                content[preLabel] = this.getContentFromArray(el_array[1], preLabel)[preLabel];
            }
            line_level += 1;
        });
        return content;
    },

    formatContentValue: function (memory_obj) {
        var content = '';
        content = memory_obj[''];
        var sep = '\n===== Cálculos auxiliares =================================\n';
        for (var property in memory_obj) {
            if (property != '') {
                content += sep;
                content += memory_obj[property];
                sep = '\n--------------------------------------------------------\n';
            }
        }
        return content;
    },

    getMemoryContent: function (cfg) {
        if (!this._editorXml) {
            var contentValue = this.formatContentValue(this.getContentFromArray(cfg.content));
            this._editorXml = Ext._create(
                "core.fields.CodeEditor",
                Ext.apply(this.codeEditorCustomConfig, {
                    value: contentValue,
                })
            );
        }

        return this._editorXml;
    },

    getMemoryPanel: function (cfg) {
        if (!this._editorMemoryPanel) {
            this._editorMemoryPanel = Ext._create("Ext.Panel", {
                // title: "XML - Conteúdo",
                flex: 1,
                border: false,
                items: [this.getMemoryContent(cfg)],
            });
        }

        return this._editorMemoryPanel;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: "Memória de cálculo",
        });

        Ext.apply(cfg, {
            width: 600,
            height: 650,
            scope: this,
            autoScroll: true,
            layout: {
                type: "hbox",
                align: "stretch",
            },
            border: false,
            items: [
                this.getMemoryPanel(cfg)
                // {
                //     xtype: "tabpanel",
                //     height: 700,
                //     activeItem: 0,
                //     items: [
                //         this.getMemoryPanel(cfg),
                //     ],
                // },
            ],
        });
        rh.gfp.paycheck.EntriesMemoryWindow.superclass.constructor.call(this, cfg);
    },
});
