
Ext.ns('toolkit.fields');
Ext.ns('toolkit.plugins');

toolkit.fields.CKEditor = Ext.extend(
    Ext.form.TextArea,
    {
        setValue: function(value, propagate) {
            propagate = (propagate !== undefined ? propagate : true);

            try {
                if(propagate && this._editor) {
                    this._editor.setData(value || '');
                } else if(propagate && !this._editor) {
                    var task = null;
                    var recoveyCount = 0;

                    task = Ext.TaskMgr.start({
                        interval: 500,
                        repeat: 6,
                        scope: this,
                        run: function() {
                            console.log('#ckeditor #setValue #recoveyCount %d', ++recoveyCount);

                            if (this._editor) {
                                this._editor.setData(value || '');
                                Ext.TaskMgr.stop(task);
                            }
                        }
                    });
                }
            }
            catch(e) {
                console.debug(e);
            }
            finally {
                toolkit.fields.CKEditor.superclass.setValue.call(this, value);
            }
        },

        setWidth: function(value) {
            this.width = value;
            this._editor.resize(this.height, this.height, true);
        },

        setHeight: function(value) {
            this.height = value;
            this._editor.resize(this.width, this.height, true);
        },

        destroy: function() {
            try {
                if(this._editor)
                    this._editor.destroy();

                toolkit.fields.CKEditor.superclass.destroy.call(this);
            }
            catch(e) {
                console.error(e);
            }
        },

        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});

            Ext.applyIf(cfg, {
                scope: this,
                listeners: {
                    render: function(panel) {
                        var config = Ext.applyIf(
                            (this.editorConfig || {}),
                            {
                                toolbarCanCollapse: true,
                                removeButtons: 'Subscript,Superscript,Styles,HorizontalRule',
                                toolbarGroups: panel.toolbarGroups ? panel.toolbarGroups :[
                                    {name: 'styles', itens: ['Format']},
                                    {name: 'clipboard'},
                                    {name: 'editing'},
                                    {name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ]},
                                    {
                                        name: 'paragraph',
                                        groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                                    },
                                    // {name: 'others'},
                                    {name: 'links'},
                                    {name: 'insert'},
                                    {name: 'tools'},
                                    {name: 'document', groups: ['mode', 'save']}
                                ],
                                resize_enabled: false,
                                height: panel.height,
                                width: panel.width,
                                disableNativeSpellChecker: false,
                                startupFocus: (panel.startupFocus != false),
                                removePlugins : 'tabletoolstoolbar,tableresizerowandcolumn,tableresize,tableselection,tabletools,contextmenu',
                                resize_dir: (!panel.height && !panel.width ? 'both' : null),
                                basicEntities: true,
                                format_tags: CKEDITOR.config.format_tags,
                                coreStyles_bold: { element: 'b', overrides: 'strong' },
                                coreStyles_italic: { element : 'i', overrides : 'em' },
                                // extraPlugins: 'textindent'
                            }
                        );

                        if(panel.toolbar) {
                            console.warn('O uso de toolbar no CKEditor é deprecated, no seu lugar use toolbarGroups');
                            console.warn('Toolbar', panel.toolbar);
                        }

                        panel._editor = CKEDITOR.replace(panel.getEl().dom, config);

                        var cb = function(e) {
                            if(panel._editor.checkDirty()) panel.setValue(panel._editor.getSnapshot(), false);
                        };

                        var mask = new Ext.LoadMask(panel.ownerCt.getEl(), {msg: 'preparando o editor...'});
                        mask.show();
                        panel._editor.on('instanceReady', function() {
                            try {
                                var value = panel.getValue();
                                try {
                                    panel._editor.loadSnapshot(value || '');
                                } catch(e) {
                                    var task = null;
                                    var recoveyCount = 0;

                                    task = Ext.TaskMgr.start({
                                        interval: 500,
                                        repeat: 6,
                                        run: function() {
                                            var value = panel.getValue();

                                            console.log('#ckeditor #onload #recoveyCount %d', ++recoveyCount);

                                            if (value) {
                                                panel._editor.loadSnapshot(value);
                                                Ext.TaskMgr.stop(task);
                                            }
                                        }
                                    });
                                }

                            }
                            catch(e) {
                                console.log(e);
                            }
                            finally {
                                mask.hide();
                            }
                        });

                        panel._editor.on('change', cb, panel);

                        Ext.each(panel.editorEvents || [], function(evt) {
                            panel._editor.on(
                                evt.name,
                                evt.handler,
                                evt.scope || window
                            );
                        });
                    }
                }
            });

            toolkit.fields.CKEditor.superclass.constructor.call(this, cfg);
        }
    }
);

toolkit.plugins.CKEditor = toolkit.fields.CKEditor;

Ext.reg('ckeditor', toolkit.fields.CKEditor);
