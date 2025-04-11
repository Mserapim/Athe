/**
 *
 **/
Ext._define('core.fields.CodeEditor', {
    extend: 'Ext.form.TextArea',

    xtype: 'codefield',

    setValue: function(value) {
        if(this._codeMirror)
            this._codeMirror.setValue(value);
        else
            core.fields.CodeEditor.superclass.setValue.call(this, value);
    },

    setSize: function(width, height) {
        if(width && height)
            this._codeMirror.setSize(width, height);
        else
            this._codeMirror.setSize(width);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
            }
        );

        cfg.editorConf = core.nullValue(cfg.editorConf, {});
        Ext.applyIf(
            cfg.editorConf,
            {
                mode: 'text/html',
                keyMap: 'sublime',
                indentUnit: 4,
                lineNumbers: true,
                foldGutter: true,
                autoCloseBrackets: true,
                matchBrackets: true,
                lineWrapping: true,
                showCursorWhenSelecting: true,
                lint: true,
                extraKeys: {"Ctrl-Space": "autocomplete"},
                gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter', 'CodeMirror-lint-markers'],
            }
        );

        /*
            value: value,
        */

        Ext.apply(
            cfg,
            {
            }
        );

        // this.callParent([cfg]);
        core.fields.CodeEditor.superclass.constructor.call(this, cfg);

        this.on({
            scope: this,
            render: function(text) {
                var self = this;

                this._codeMirror = CodeMirror.fromTextArea(
                    text.getEl().dom,
                    this.editorConf
                );

                this._codeMirror.setValue(text.getValue());

                this._codeMirror.on('change', function(editor, evt) {
                    text.getEl().dom.value = editor.getValue();
                });

                core.nullValue(this.editorEvents, []).forEach(
                    function(item) {
                        this._codeMirror.on(
                            item.name,
                            function() {
                                item.handler.call(item.scope || window, arguments);
                            }
                        );
                    },
                    this
                );

                this.setSize(text.getBox().width, text.getBox().height);
            }
        });
    }
});
