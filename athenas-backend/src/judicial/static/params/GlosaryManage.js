/**
 *
 **/
Ext._define('judicial.params.GlosaryManage', {
    extend: 'toolkit.widget.TabPanel',

    observeGlosary: function() {
        var value = this.glosary();

        if(value) {
            this.getTemplateGrid().setParam('glosary', value);
            this.getTemplateGrid().setFilterProperty('glosary', value, 1);
            this.getTemplateGrid().enable();
        }
        else {
            this.getTemplateGrid().setParam('glosary', null);
            this.getTemplateGrid().removeFilterProperty('glosary', value, false);
            this.getTemplateGrid().getStore().removeAll();
            this.getTemplateGrid().disable();
        }

        this.template(null);
    },

    observeTemplate: function() {
        var value = this.template();
        var template = this.templateDefinition();

        if(value)
            this.getEditorPanel().enable();
        else
            this.getEditorPanel().disable();
    },

    templateDefinition: function(value) {
         if(value !== undefined) {
             this._templateDefinition = value;
         }

         return this._templateDefinition;
     },

    template: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._template = value;

            if(!prevent) this.observeTemplate();
        }

        return this._template;
    },

    glosary: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._glosary = value;

            if(!prevent) this.observeGlosary();
        }

        return this._glosary;
    },

    getGlosaryGrid: function() {
        if(!this._glosaryGrid) {
            this._glosaryGrid = Ext._create('judicial.params.GlosaryGrid', {
                width: 320,
                margins: '0 4 0 0'
            });

            this._glosaryGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(self, rowIndex, data) {
                    this.glosary(data.get('pk'));
                },
                rowdeselect: function() {
                    this.glosary(null);
                }
            });
        }

        return this._glosaryGrid;
    },

    getTemplateGrid: function() {
        if(!this._templateGrid) {
            this._templateGrid = Ext._create('judicial.params.GlosaryTemplateGrid', {
                width: 320,
                margins: '0 4 0 0',
                gridAutoLoad: false
            });

            this._templateGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(self, rowIndex, data) {
                    this.template(data.get('pk'));
                    this.getEditor().setValue(data.get('template'));
                },
                rowdeselect: function() {
                    this.template(null);
                }
            });
        }

        return this._templateGrid;
    },

    updateTemplate: function() {
        var rest = Ext._create('judicial.params.GlosaryTemplateRestful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Gravando template.'});

        mask.show();
        rest.doRequest(
            rest.getRoute('update', this.template(), 'PUT', {
                params: {
                    template: this.getEditor().getValue(),
                },
                scope: this,
                callback: function() {
                    mask.hide();
                    mask = null;
                },
                success: function(xhr) {
                    this.getTemplateGrid().getStore().reload();
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Recurso indisponivel',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Não foi possivel persistir as modificações no template.'
                    });
                }
            })
        );
    },

    getEditor: function() {
        if(!this._editor) {
            this._editor = Ext._create('core.fields.CodeEditor', {
                editorConf: {
                    mode: 'text/x-django'
                },
                editorEvents: [
                    {
                        name: 'change',
                        handler: function() {
                            this.taskCountdown.active = true;
                            this.taskCountdown.count = this.taskCountdown.countMax;
                        },
                        scope: this
                    },
                ],
                width: '100%',
                height: '100%'
            });

            var self = this;
            this.taskCountdown = {
                active: false,
                count: 0,
                countMax: 3,
                run: function() {
                    if(self.taskCountdown.active && self.taskCountdown.count > 0) {
                        self.taskCountdown.count--;
                    }

                    if(self.taskCountdown.active && self.taskCountdown.count === 0) {
                        self.taskCountdown.active = false;
                        self.taskCountdown.count = 0;
                        self.updateTemplate();
                    }

                },
                interval: 1000
            };

            Ext.TaskMgr.start(this.taskCountdown);
        }

        return this._editor;
    },

    getEditorPanel: function() {
        if(!this._editorPanel) {
            this._editorPanel = Ext._create('Ext.Panel', {
                flex: 1,
                border: false,
                items: [
                    this.getEditor()
                ]
            });
        }

        return this._editorPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Glosario'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                border: false,
                items: [
                    this.getGlosaryGrid(),
                    this.getTemplateGrid(),
                    this.getEditorPanel()
                ]
            }
        );

        // this.callParent([cfg]);
        judicial.params.GlosaryManage.superclass.constructor.call(this, cfg);

        this.glosary(null);
    }
});
