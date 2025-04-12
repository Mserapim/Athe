Ext._define('rh.reports.EmployeeBirthday', {
    extend: 'toolkit.widget.TabPanel',

	_buildReport: function(type){
        var month = this.getMonths().getValue();

        engine.mq.Report.request({
            report: '/to/mpe/rh/servidor/lista_servidor/data_nascimento',
            waitMessage: 'Gerando relatório...',
            params: {
                outfile: 'aniversariantes',
                report_name: 'Relatório de Aniversariantes - Servidores/Membros',
                mes: month,
                tipo: this.getType().getValue()
            }
        }, type);
    },

    getType: function(){
        if(!this._ativo){
            this._ativo = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Tipo',
                hiddenName: 'type',
                triggerAction: 'all',
                store: [
                    ['T', 'Todos'],
                    ['S', 'Servidor'],
                    ['M', 'Membro'],
                ],
                anchor: '99%'
            });
        }

        return this._ativo;
    },

    getMonths: function () {
        if (!this._monthField) {
            this._monthField = new Ext.form.ComboBox({
                fieldLabel: 'Mês',
                hiddenName: 'mes',
                anchor: '99%',
                store: [
                    ['T', 'TODOS'],
                    [1, 'JANEIRO'],
                    [2, 'FEVEREIRO'],
                    [3, 'MARÇO'],
                    [4, 'ABRIL'],
                    [5, 'MAIO'],
                    [6, 'JUNHO'],
                    [7, 'JULHO'],
                    [8, 'AGOSTO'],
                    [9, 'SETEMBRO'],
                    [10, 'OUTUBRO'],
                    [11, 'NOVEMBRO'],
                    [12, 'DEZEMBRO'],
                ],
                triggerAction: 'all',
                mode: 'local'
            });
        }
        return this._monthField;
    },

	getMain: function(){
		if(!this._panel)
		this._panel = new Ext.Panel({
		    layout: 'border',
		    region: 'center',
		    height: 650,
		    split: true,
		    autoEl: {tag: 'center'},
		    items: [
	        {
	        	region: 'center',
	        	border: false,
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		title: 'Lista dos Aniversariantes',
	        		name: 'fieldServidor',
	        		width: "33%",
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
                        this.getMonths(),
                        this.getType(),
                        {
                            xtype: 'button',
                            iconCls: 'icon-siatu icon-siatu-move-down',
                            style: 'margin-top: 10px',
                            text: 'Gerar Relatório',
                            width: 100,
                            height: 25,
                            scope: this,
                            menu: {
                                scope: this,
                                items: [
                                    {
                                        text: 'Arquivo PDF ',
                                        type: 'PDF',
                                        iconCls: 'icon-ged icon-ged-application-pdf',
                                        scope: this,
                                        handler: function (item) {
                                            this._buildReport(item.type);
                                        }
                                    },
                                    {
                                        text: 'Arquivo ODT',
                                        type: 'ODT',
                                        iconCls: 'icon-ged icon-ged-application-msword',
                                        scope: this,
                                        handler: function (item) {
                                            this._buildReport(item.type);
                                        }
                                    },
                                    {
                                        text: 'Arquivo XLS',
                                        type: 'XLS',
                                        iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                        scope: this,
                                        handler: function (item) {
                                            this._buildReport(item.type);
                                        }
                                    },
                                ]
                            },
                        }
	        		]
	        	},
        		]
        	}
    		]
	    });

		return this._panel;
	},


	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Relatório -> Aniversariantes'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[
					this.getMain(),
				]
			}
		);

		// this.getCurrentPayroll();

		rh.reports.EmployeeBirthday.superclass.constructor.call(this, cfg);
	}
});