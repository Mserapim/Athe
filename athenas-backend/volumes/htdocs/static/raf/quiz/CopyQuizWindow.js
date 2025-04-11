Ext._define('raf.quiz.CopyQuizWindow', {
    extend: 'Ext.Window',

    copy: function() {
        var rest = Ext._create('raf.quiz.Restful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Copiando questionário...'});
        var values = this.getFormPanel().getForm().getValues();
        mask.show();
        rest.copyQuiz(
            values,
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();

                        Ext.Msg.show({
                            title: 'Copiando questionário',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Copiando questionário',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Copiando questionário',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getTypeQuizField: function() {
        if(!this._typeQuizField) {
            this._typeQuizField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Tipo de questionário",
                allowBlank: false,
                rest: "raf.typequiz.Restful",
                name: "typequiz",
                disabled: false,
                gridConfig: {
                    columnAction: false
                }
            });
        }

        return this._typeQuizField;
    },

    getYearBaseField: function() {
        if(!this._yearBaseField) {
            this._yearBaseField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Ano Base",
                allowBlank: false,
                rest: "raf.yearbase.Restful",
                name: "yearbase",
                disabled: false,
                columnAction: false,
                gridConfig: {
                    columnAction: false
                }
            });
        }

        return this._yearBaseField;
    },


    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'Questionário',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                            {
                                xtype: 'displayfield',
                                name: 'quiz_unicode',
                                hideLabel: true,
                            },
                        ]
                    },
                    {
                        xtype: "hidden",
                        name: "quiz",
                    },
                    this.getTypeQuizField(),
                    this.getYearBaseField(),
                ]
            });

        return this._formPanel;
    },


    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Copiar questionário',
            modal: true,
            width: Ext.getBody().getBox().width * 0.4,
        });

        Ext.apply(cfg, {

            items: [
                this.getFormPanel(cfg)
            ],
            buttons: [
                {
                    text: 'Copiar',
                    scope: this,
                    handler: function() { this.copy(); }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });

        raf.quiz.CopyQuizWindow.superclass.constructor.call(this, cfg);

        this.getFormPanel().getForm().setValues(
            {
                quiz: this.params.quiz,
                quiz_unicode: this.params.quiz_unicode
            }
        );
    }
});
