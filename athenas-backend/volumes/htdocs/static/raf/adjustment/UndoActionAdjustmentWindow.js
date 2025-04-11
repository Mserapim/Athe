Ext._define('raf.adjustment.UndoActionAdjustmentWindow', {
    extend: 'Ext.Window',


    undoAction: function() {
        var rest = Ext._create('raf.adjustment.AdjustmentInternalControlRestful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Desfazendo decisão da solicitação...'});
        var values = this.getFormPanel().getForm().getValues();

        values.adjustment_list = (this.values.adjustment_list || 0);

        mask.show();
        rest.undoAction(
            values,
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();

                        Ext.Msg.show({
                            title: 'Desfazer decisão',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Desfazer decisão',
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
                        title: 'Desfazer decisão',
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

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    // {
                    //     xtype:'fieldset',
                    //     title: 'Atividade',
                    //     collapsible: false,
                    //     autoHeight:true,
                    //     items: [
                    //         {
                    //             xtype: 'displayfield',
                    //             name: 'activity_unicode',
                    //             hideLabel: true,
                    //         },
                    //     ]
                    // },
                    {
                        xtype:'fieldset',
                        title: 'Parecer',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                           {
                               fieldLabel: "Resposta",
                               xtype: "ckeditor",
                               hideLabel: true,
                               allowBlank: false,
                               name: "answer",
                               submit: true,
                               toolbarGroups: [
                                   {name: 'styles', itens: ['Format']},
                                   {name: 'clipboard'},
                                   {name: 'editing'},
                                   {name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ]},
                                   {
                                       name: 'paragraph',
                                       groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                                   },
                               ],
                           }
                        ]
                    },
                ]
            });

        return this._formPanel;
    },


    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Desfazer decisão da solicitação',
        });

        Ext.apply(cfg, {
            width: 800,
            items: [
                this.getFormPanel(cfg)
            ],
            buttons: [
                {
                    text: 'Desfazer decisão',
                    scope: this,
                    handler: function() { this.undoAction(); }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });


        raf.adjustment.UndoActionAdjustmentWindow.superclass.constructor.call(this, cfg);

        this.getFormPanel().getForm().setValues(this.values !== undefined ? this.values : {});
    }
});
