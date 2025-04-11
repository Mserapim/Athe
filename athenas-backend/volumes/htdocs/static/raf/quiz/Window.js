Ext._define('raf.quiz.Window', {
    extend: 'core.RestfulWindow',

    rest: 'raf.quiz.Restful',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            width: 600,
            height: 425,
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.quiz(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        raf.quiz.Window.superclass.constructor.call(this, cfg);

        if(cfg.oId || this.oId) this.quiz(cfg.oId || this.oId);

        this.quiz(cfg.oId === undefined ? null : cfg.oId);
    },

    quiz: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._quiz = value;

            if(dispatch) this.observerQuiz();
        }

        return this._quiz;
    },

    observerQuiz: function() {
        var value = this.quiz();

        if(value)
            this.getLegalClassField().objectId(value);
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

    getLegalClassField: function(cfg) {
        if(!this._legalClassField)
            this._legalClassField = Ext._create('core.fields.RelatedRestfulField', {
                title: 'Classes',
                hideLabel: true,
                name: 'legalclasses',
                displayField: 'unicode',
                allowBlank: true,
                relatedname: 'quizzes',
                rest: this.rest,
                sourceRest: 'judicial.taxonomy.LegalClassRestful',
                oId: this.oId || cfg.oId,
                width: 588,
                height: 250,
                border: false
            });

        return this._legalClassField;
    },

    getExcludeLegalClassField: function(cfg) {
        if(!this._excludeClassField)
            this._excludeClassField = Ext._create('core.fields.RelatedRestfulField', {
                title: 'Exceção',
                hideLabel: true,
                name: 'exclude_classes',
                displayField: 'unicode',
                allowBlank: true,
                relatedname: 'exclude_quizzes',
                rest: this.rest,
                sourceRest: 'judicial.taxonomy.LegalClassRestful',
                oId: this.oId || cfg.oId,
                width: 588,
                height: 250,
                border: false
            });

        return this._excludeClassField;
    },

    getQuizPanel: function() {
        if(!this._quizPanel)
            this._quizPanel = Ext._create('Ext.Panel',{
                layout: 'form',
                border: false,
                frame: true,
                items: [
                    this.getTypeQuizField(),
                    this.getYearBaseField(),
                    {
                        xtype: 'panel',
                        frame: false,
                        border: false,
                        layout: {
                            type: 'hbox',
                            align: 'stretch'
                        },
                        defaults: { flex: 1.0 },
                        height: 25,
                        items: [
                            {
                                xtype: 'checkbox',
                                name: 'activated',
                                boxLabel: 'Ativo',
                                checked: true
                            }
                        ]
                    }
                ]
            });
        return this._quizPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                items: [
                    this.getQuizPanel(),
                    {
                        xtype: 'tabpanel',
                        activeTab: 0,
                        autoHeight: true,
                        items: [
                            this.getLegalClassField(cfg),
                            this.getExcludeLegalClassField(cfg),
                        ]
                    }
                ]
            });

        return this._formPanel;
    }
});
