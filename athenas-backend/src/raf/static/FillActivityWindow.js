Ext._define('raf.FillActivity.Window', {
    extend: 'Ext.Window',

    makeValues: function(cfg) {
        return {
            quiz: cfg.values.quiz_obj.data.pk,
            quiz_unicode: cfg.values.quiz_obj.data.typequiz_unicode,
            // quiz_list_classes: cfg.values.quiz_obj.data.list_classes,
            workerlocation: cfg.values.workerlocation_obj.data.pk,
            workerlocation_unicode: cfg.values.workerlocation_obj.data.location_unicode,
        };
    },

    getActivityForm: function(cfg) {
        if(!this._activityForm) {
            this._activityForm = Ext._create('raf.FillActivity.Grid', {
                layout: 'fit',
                height: 450,
                params: this.makeValues(cfg)
            });
        }

        return this._activityForm;
    },

    getFormPanel: function(cfg) {
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
                        items:[
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Questionário',
                                name: 'quiz',
                                hideLabel: true,
                            },
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Promotoria',
                                name: 'workerlocation',
                                hideLabel: true,
                            },
                        ]
                    },
                    this.getActivityForm(cfg)
                ]
            });

        return this._formPanel;
    },

    openSearchProcessNumber: function() {
        Ext._create('raf.searchprocessnumber.SearchProcessNumberWindow', {
            values: { }
        }).show();
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Preencher Questionário',
            width: 900,
            height: 600,
        });

        Ext.apply(cfg, {
            items: [
                this.getFormPanel(cfg),
            ],
            buttons: [
                {
                    text: 'Pesquisar por número',
                    scope: this,
                    handler: function() { this.openSearchProcessNumber(); }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });


        raf.FillActivity.Window.superclass.constructor.call(this, cfg);

        this.getFormPanel().getForm().setValues(
            {
                quiz: this.values.quiz_obj.data.typequiz_unicode,
                workerlocation: this.values.workerlocation_obj.data.location_unicode
            }
        );
    }
});
