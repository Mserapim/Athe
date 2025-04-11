Ext._define('rh.pvf.myrights.AcquisitionPeriodGrid', {
  extend: 'core.RestfulGrid',

  rest: 'rh.pvf.myrights.AcquisitionPeriodRestful',

  getColumnModel: function () {
    if (!this._columnModel)
      this._columnModel = Ext._create(
        'Ext.grid.ColumnModel',
        [
          Ext._create('Ext.grid.RowNumberer'),
          { header: 'Cod', dataIndex: 'pk', width: 50, hidden: true },
          { header: 'Situação', dataIndex: 'status_display',hidden: true, width: 200, id: 'autoExpandColumn' },
          { header: 'Nome do Grupo', dataIndex: 'group_period_unicode', width: 200 },
          { header: 'Início da Fruição', dataIndex: 'start_date_fruition', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
          { header: 'Início Aquisitivo', dataIndex: 'start_date_acquisition', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
          { header: 'Fim Aquisitivo', dataIndex: 'end_date_acquisition', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
          { header: 'Total em dias', dataIndex: 'days', width: 120 },
          { header: 'Total agendado', dataIndex: 'booked_days_cache', width: 100},
          { header: 'A usufruir', dataIndex: 'days_to_enjoy_cache', width: 70,hidden: true },
          { header: 'Saldo', dataIndex: 'days_not_booked_cache', width: 90 },
          { header: 'Dias vendidos', dataIndex: 'paid_days_cache', width: 90, hidden: true },
        ]
      );

    return this._columnModel;
  },

  getToolbar: function (cfg) {
    if (!this._toolbar) {
      cfg = core.nullValue(cfg, {});
      Ext.apply(cfg, { gridAutoLoad: false, });

      this._toolbar = rh.afastamento.ManagerGrid.superclass.getToolbar.call(this, cfg);
      this._toolbar.insert(0,
        {
          text: 'Anexos',
          iconCls: true,
          icon: "/" + global.Context + "/static/engine/images/icons/athenas-0246.png",
          handler: function () {
            var selected = this.getSelectionModel().getSelected();
            console.log(selected)
            if (!selected) {
              Ext.Msg.show({
                title: "Anexos",
                width: 250,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: "Selecione um item",
              });
            } else {
              new rh.pvf.myrights.AttachmentWindow({},{
                acquisition_period_pk: this.getSelectionModel().getSelected().data.pk,
                callback: this.getStore()
              }).show();
            }            
          },
          scope: this
        }
      );
    }
    return this._toolbar;
  },
});

core.RestfulGrid.register(
  'rh.pvf.myrights.AcquisitionPeriodRestful',
  'rh.pvf.myrights.AcquisitionPeriodGrid'
);

