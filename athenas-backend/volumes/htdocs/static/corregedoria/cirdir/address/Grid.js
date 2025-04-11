Ext._define('corregedoria.cirdir.address.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'corregedoria.cirdir.address.Restful',
    restWindow: 'corregedoria.cirdir.address.Window',

    configOrderToolBar: ['add', 'edit', 'remove', 'history', '->','submit', ],

    mixins: {'1': 'corregedoria.cirdir.ActionsMixin'},

    getHistoryAction: function(cfg) {
        if(!this._historyAction){
            this._historyAction = new Ext.Button({
                xtype: 'button',
                text: ' Histórico',
                iconCls: 'icon-crgmpe icon-crgmpe-list',
                handler: function() {
                    Ext._create('corregedoria.cirdir.HistoryWindow', {
                        params: {
                          controlinformation: cfg.params.controlinformation,
                          criteria_key: 1,
                        },
                    }).show();
                }
            });
        }
        return this._historyAction;
    },

    getSubmitAction: function(cfg) {
        if(!this._submitAction){
            this._submitAction = new Ext.Button({
                xtype: 'button',
                text: ' Submeter Residência',
                iconCls: 'icon-crgmpe icon-crgmpe-success',
                disabled: cfg.params.closed_address,
                handler: function() {
                  Ext.Msg.show({
                      title: 'Submeter Residência',
                      msg: 'Tem certeza que deseja submeter as informações de Residência?',
                      icon: Ext.Msg.QUESTION,
                      buttons: Ext.Msg.YESNO,
                      scope: this,
                      fn: function(btn) {
                          if(btn=='no') return;
                          Ext.Ajax.request({
                              scope: this,
                              url: core.callAction('CIRDIRControlInformation', 'submit'),
                              callback: function() {
                                  cfg.params.mainGrid.getStore().reload();
                              },
                              success: function(request) {
                                  var rst = Ext.decode(request.responseText);
                                  if (rst.success == true) {
                                      Ext.Msg.show({
                                          title: 'Submeter Residência',
                                          msg: rst.message,
                                          icon: Ext.Msg.INFO,
                                          buttons: Ext.Msg.OK
                                      });
                                  } else {
                                      Ext.Msg.show({
                                          title: 'Submeter Residência',
                                          msg: rst.message,
                                          icon: Ext.Msg.ERROR,
                                          buttons: Ext.Msg.OK
                                      });
                                  }
                                  core.invokeCallback((this.callback || {}).success);
                              },
                              failure: function(request) {
                                  var rst = Ext.decode(request.responseText);
                                  Ext.Msg.show({
                                      title: 'Submeter Residência',
                                      msg: rst.message,
                                      icon: Ext.Msg.ERROR,
                                      buttons: Ext.Msg.OK
                                  });
                              },
                              params: {
                                  controlinformation: cfg.params.controlinformation,
                                  criteria: 'address',
                              },
                          });
                      }
                  });
                }
            });
        }
        return this._submitAction;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 30, renderer: core.rendererIconGrid},
                    {header: 'Endereço', dataIndex: 'ref_address_unicode', id: 'autoExpandColumn', },
                    {header:'Ações', dataIndex: 'actions', xtype: 'actioncolumn', scope: this, width: 60, items: this.columnActionAceptAndEdit() }
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.address.Restful',
    'corregedoria.cirdir.address.Grid'
);
