Ext._define('rh.pvf.myrights.UsufructGrid', {
  extend: 'core.RestfulGrid',

  rest: 'rh.pvf.myrights.UsufructRestful',

  configOrderToolBar: ['attachments'],

  getColumnModel: function () {
    if (!this._columnModel)
      this._columnModel = Ext._create(
        'Ext.grid.ColumnModel',
        [
          { header: 'Cod', dataIndex: 'pk', width: 50, hidden: true },
          {
            id: 'icons',
            dataIndex: 'icons',
            header: '',
            width: 100,
            sortable: false,
            renderer: toolkit.util.formatStatus,
            menuDisabled: true
          },
          { header: 'Situação', dataIndex: 'status_display', id: 'autoExpandColumn' },

          { header: 'Atividade', dataIndex: 'activity_unicode', width: 300, hidden: true },
          { header: 'Início', dataIndex: 'start_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
          { header: 'Fim', dataIndex: 'end_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
          { header: 'Dias programados/Vendidos', dataIndex: 'days', width: 160 },
        ]
      );

    return this._columnModel;
  },

  // getToolbar: function (cfg) {
  //   if (!this._toolbar) {
  //     cfg = core.nullValue(cfg, {});
  //     Ext.apply(cfg, { gridAutoLoad: false, });

  //     this._toolbar = rh.afastamento.ManagerGrid.superclass.getToolbar.call(this, cfg);
  //     this._toolbar.insert(0,
  //       {
  //         text: 'Anexos',
  //         iconCls: true,
  //         icon: "/" + global.Context + "/static/engine/images/icons/athenas-0246.png",
  //         handler: function () {
  //           var selected = this.getSelectionModel().getSelected();
  //           if (!selected) {
  //             Ext.Msg.show({
  //               title: "Anexos",
  //               width: 250,
  //               icon: Ext.Msg.ERROR,
  //               buttons: Ext.Msg.OK,
  //               msg: "Selecione um item",
  //             });
  //           } else {
  //             new rh.pvf.myrights.AttachmentWindow({},{
  //               acquisition_period_pk: this.getSelectionModel().getSelected().json.acquisition_period,
  //               callback: this.getStore()
  //             }).show();
  //           }            
  //         },
  //         scope: this
  //       }
  //     );
  //   }
  //   return this._toolbar;
  // },
});

core.RestfulGrid.register(
  'rh.pvf.myrights.UsufructRestful',
  'rh.pvf.myrights.UsufructGrid'
);
