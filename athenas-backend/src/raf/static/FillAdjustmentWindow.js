Ext._define('raf.FillAdjustmentWindow', {
    extend: 'Ext.Window',

    // width: 800,

    // newObject: function() {
    //     var rest = Ext._create('raf.activity.AdjustmentRestful');
    //     var values = this.getFormPanel().getForm().getValues();
    //     rest.newObject(
    //         values,
    //         {
    //             scope: this,
    //             fn: function(rst) {
    //                 if(rst.success) {
    //                     var params = {};
    //                     params.conversation = rst.conversation;
    //                     params.origin = rst.origin;
    //                     params.message = values.justification;

    //                     this.conversation(params);
    //                 }
    //                 else
    //                     Ext.Msg.show({
    //                         title: 'Solicitação de Ajuste',
    //                         msg: rst.message,
    //                         icon: Ext.Msg.ERROR,
    //                         buttons: Ext.Msg.OK
    //                     });
    //             }
    //         },
    //         {
    //             scope: this,
    //             fn: function(message) {
    //                 Ext.Msg.show({
    //                     title: 'Solicitação de Ajuste',
    //                     msg: message,
    //                     icon: Ext.Msg.ERROR,
    //                     buttons: Ext.Msg.OK
    //                 });
    //             }
    //         },
    //         {
    //             scope: this,
    //             fn: function() {}
    //         }
    //     );
    // },

    // conversation: function(params) {
    //     var rest = Ext._create('raf.conversation.Restful');
    //     var mask = new Ext.LoadMask(this.getEl(), {msg: 'Enviando menssagem...'});

    //     mask.show();
    //     rest.conversation(
    //         params,
    //         {
    //             scope: this,
    //             fn: function(rst) {
    //                 if(rst.success) {
    //                     core.invokeCallback((this.callback || {}).success);
    //                     this.close();
    //                 } else
    //                     Ext.Msg.show({
    //                         title: 'Enviando menssagem',
    //                         msg: rst.message,
    //                         icon: Ext.Msg.ERROR,
    //                         buttons: Ext.Msg.OK
    //                     });
    //             }
    //         },
    //         {
    //             scope: this,
    //             fn: function(message) {
    //                 Ext.Msg.show({
    //                     title: 'Enviando menssagem',
    //                     msg: message,
    //                     icon: Ext.Msg.ERROR,
    //                     buttons: Ext.Msg.OK
    //                 });
    //             }
    //         },
    //         {
    //             scope: this,
    //             fn: function() {
    //                 mask.hide();
    //             }
    //         }
    //     );
    // },

    // getFormPanel: function(cfg) {
    //     if(!this._formPanel)
    //         this._formPanel = Ext._create('Ext.form.FormPanel', {
    //             border: false,
    //             frame: true,
    //             items: [
    //                 {
    //                     xtype: 'displayfield',
    //                     fieldLabel: 'Promotoria',
    //                     name: 'workerlocation_unicode',
    //                 },
    //                 {
    //                     xtype: 'hidden',
    //                     name: 'workerlocation',
    //                 },
    //                 {
    //                     xtype: 'displayfield',
    //                     fieldLabel: 'Item',
    //                     name: 'item_unicode',
    //                 },
    //                 {
    //                     xtype: 'hidden',
    //                     name: 'item',
    //                 },
    //                 {
    //                     xtype: 'displayfield',
    //                     fieldLabel: 'SubItem',
    //                     name: 'subitem_unicode',
    //                 },
    //                 {
    //                     xtype: 'hidden',
    //                     name: 'subitem',
    //                 },
    //                 {
    //                     xtype: 'hidden',
    //                     name: 'activity',
    //                 },
    //                 {
    //                     xtype: "displayfield",
    //                     fieldLabel: "Qtd. aferida",
    //                     name: "activity_amount",
    //                 },
    //                 {
    //                     xtype: "numberfield",
    //                     fieldLabel: "Nova Quantidade",
    //                     allowBlank: false,
    //                     allowNegative: false,
    //                     allowDecimals: false,
    //                     name: "amount",
    //                 },
    //                 {
    //                     xtype: "htmleditor",
    //                     name: "justification",
    //                     hideLabel: true,
    //                     width: 770,
    //                     enableAlignments : true,
    //                     enableColors : false,
    //                     enableFont : true,
    //                     enableFontSize : false,
    //                     enableFormat : false,
    //                     enableLinks : false,
    //                     enableLists : true,
    //                     enableSourceEdit : false,
    //                 }
    //             ]
    //         });

    //     return this._formPanel;
    // },


    // constructor: function(cfg) {
    //     cfg = core.nullValue(cfg, {});

    //     Ext.applyIf(cfg, {
    //         title: 'Ajustar Atividade',
    //     });

    //     Ext.apply(cfg, {
    //         width: 800,
    //         items: [
    //             this.getFormPanel()
    //         ],
    //         buttons: [
    //             {
    //                 text: 'Salvar',
    //                 scope: this,
    //                 handler: function() { this.newObject() }
    //             },
    //             {
    //                 text: 'Fechar',
    //                 scope: this,
    //                 handler: function() { this.close(); }
    //             }
    //         ]
    //     });


    //     raf.FillAdjustmentWindow.superclass.constructor.call(this, cfg);

    //     this.getFormPanel().getForm().setValues(this.values !== undefined ? this.values : {});
    // }
});
