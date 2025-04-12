/**
 *
 **/

Ext._define('rh.gfp.reports.ProofOfIncome', {
	extend: 'toolkit.widget.TabPanel',

	_buildPaycheck: function (paycheck) {

		var employee = this.getEmployeeField().getComboField().lastSelectionText;
		var declaration = this.getDeclarationField().getComboField().lastSelectionText;

		selected = this.getEmployeeField().getComboField().getStore().find('pk', this.getEmployeeField().getValue());

		if(this.getEmployeeField().getValue() != ''){
			pessoa_fisica = this.getEmployeeField().getComboField().getStore().getAt(selected).data.pessoa_fisica;
		}
		else if(this.getPersonField().getValue() != ''){
			pessoa_fisica = this.getPersonField().getValue();
		}
		else{
			Ext.Msg.show({
                title: 'Aviso',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'É necessário preencher Servidor Ou Pessoa Física'
            });
            return;
		}
		if(this.getDeclarationField().getValue() == ''){
			Ext.Msg.show({
                title: 'Aviso',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'É necessário preencher Declaração'
            });
            return;
		}

		engine.mq.Report.request({
			report: '/to/mpe/gfp/comprovanterendimentos',
			waitMessage: 'Gerando relatório...',
			params: {

				outfile: 'Rendimentos ' + employee + '-' + declaration,
				report_name: 'Comprovante de Rendimentos' + ' - ' + employee + ' - ' + declaration,
				pessoa_fisica: pessoa_fisica,
				declaracao: this.getDeclarationField().getValue()
			}

		});
	},

	getEmployeeField: function () {
		if (!this._employeefield)
			this._employeefield = Ext._create('core.fields.AutocompleteField', {
				name: 'employee',
				rest: 'rh.employee.Restful',
				fieldLabel: 'Servidor',
				width: 400
			});

		return this._employeefield;
	},

	getPersonField: function () {
		if (!this._personField)
			this._personField = Ext._create('core.fields.AutocompleteField', {
				name: 'person',
				rest: "rh.person.naturalperson.Restful",
				fieldLabel: 'Pessoa Física',
				width: 400
			});

		return this._personField;
	},

	getDeclarationField: function () {
		if (!this._typefield)
			this._typefield = Ext._create('core.fields.AutocompleteField', {
				name: 'declaration',
				rest: 'rh.gfp.dirf.DeclaracaoRestful',
				fieldLabel: 'Declaração',
				width: 400
			});

		return this._typefield;
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
								title: 'Impressão do Comprovante de Rendimentos - Por Servidor ou Pessoa Física',
								name: 'fieldServidor',
								width: "33%",
								style: 'margin: 5px',
								align: 'center',
								items: [
									this.getEmployeeField(),
									this.getPersonField(),
									this.getDeclarationField(),
									{
										xtype: 'button',
										iconCls: 'icon-siatu icon-siatu-move-down',
										style: 'margin-top: 10px',
										text: 'Gerar Comprovante',
										width: 100,
										height: 25,
										scope: this,
										handler: this._buildPaycheck,
									}
								]
							}
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
				title: 'Relatório -> Comprovante de Rendimentos'
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

		rh.gfp.reports.ProofOfIncome.superclass.constructor.call(this, cfg);
	}
});