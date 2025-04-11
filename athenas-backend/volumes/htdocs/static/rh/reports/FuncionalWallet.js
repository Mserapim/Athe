/**
 *
 **/

Ext._define('rh.reports.FuncionalWallet', {
	extend: 'toolkit.widget.TabPanel',

	_buildReport: function (paycheck) {

		if (this.getEmployeersField().store.getCount() > 0) {

			var multibox_items = this.getEmployeersField().store.data.items;
			var _selecteds_employers = []

			Ext.each(multibox_items, function (item) {
				_selecteds_employers.push(item.id);
			});

			var ids = _selecteds_employers.join(',');

			engine.mq.Report.request({
				report: '/to/mpe/rh/servidor/functional_card',
				waitMessage: 'Gerando relatório...',
				params: {

					outfile: 'carteira_funcional',
					report_name: 'Carteira Funcional',
					servidores: ids,
					storagedir: this.storagedir,
				}

			});
		} else Ext.Msg.show({
			msg: 'Selecione 1 servidor ou mais',
			icon: Ext.Msg.ERROR,
			buttons: Ext.Msg.OK
		})
	},

	getEmployeersField: function () {
		if (!this._employeefield)
			this._employeefield = Ext._create('toolkit.plugins.MultiSelectField', {
				fieldLabel: 'Servidor(es)',
				name: 'Servidores',
				hiddenName: 'Servidores',
				controller: 'RHServidor',
				conf: {
					canAdd: false,
					canEdit: false
				},
				displayField: 'description',
				valueField: 'pk',
				width: 400,
				height: 400
			});


		return this._employeefield;
	},


	getMain: function () {
		if (!this._panel)
			this._panel = new Ext.Panel({
				layout: 'border',
				region: 'center',
				height: 650,
				split: true,
				autoEl: { tag: 'center' },
				items: [
					{
						// title: 'Informações do Contra-Cheque',
						region: 'center',
						border: false,
						items: [
							{
								xtype: 'fieldset',
								title: 'Geração de Carteira Funcional',
								name: 'fieldServidor',
								width: 500,
								style: 'margin: 5px',
								align: 'center',
								items: [
									this.getEmployeersField(),
									{
										xtype: 'button',
										iconCls: 'icon-siatu icon-siatu-move-down',
										style: 'margin-top: 10px',
										text: 'Gerar Relatório',
										width: 100,
										height: 25,
										scope: this,
										handler: this._buildReport,
									}
								]
							},
						]
					}
				]
			});

		return this._panel;
	},




	constructor: function (cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
				title: 'Relatório -> Geração de Carteira Funcional'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: [
					this.getMain(),
				]
			}
		);

		// this.getCurrentPayroll();
		this.storagedir = cfg.storageDir;
		rh.reports.FuncionalWallet.superclass.constructor.call(this, cfg);
	}
});