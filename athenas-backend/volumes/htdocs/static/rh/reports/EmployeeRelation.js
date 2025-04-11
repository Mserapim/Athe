/**
 *
 **/

Ext._define('rh.reports.EmployeeRelation', {
	extend: 'toolkit.widget.TabPanel',

	_buildReport: function(file_type){

		if(this.getDateExEnd().getValue() && this.getDateExStart().getValue()){
	        var employee = this.getEmployeeField().getValue() == "" ? 't' : this.getEmployeeField().getValue();
	        var jobposition = this.getJobPosition().getValue() == "" ? 't' : this.getJobPosition().getValue();
	        var especialidade = this.getEspecialidade().getValue() == "" ? 't' : this.getEspecialidade().getValue();
	        var ativo = this.getAtivo().getValue() == "" ? 't' : this.getAtivo().getValue();
	        var situation = this.getSituation().getValue() == "" ? 't' : this.getSituation().getValue();
			var type = this.getType().getValue() == "" ? 't' : this.getType().getValue();
			var employeetype = this.getEmployeeType().getValue() == "" ? 't' : this.getEmployeeType().getValue();
	        var start = new Date(this.getDateExStart().getValue()).format("Y-m-d").toString();
	        var end = new Date(this.getDateExEnd().getValue()).format("Y-m-d").toString();
	        var workplace = this.getWorkplace().getValue() == "" ? 't' : this.getWorkplace().getValue();

	        engine.mq.Report.request({
	            report: '/to/mpe/rh/servidor/Relacao_Servidores',
	            waitMessage: 'Gerando relatório...',
	            params: {

	                outfile: 'listagemdeservidores-' + start + '-' + end,
	                report_name: 'Listagem de Servidores: '  + start + ' - ' + end,
	                ativo: ativo,
	                situacao: situation,
	                cargo: jobposition,
	                especialidade: especialidade,
	                lotacao: workplace,
	                tipo: type,
	                servidor: employee,
	                tipo_servidor: employeetype,
	                data_exercicio_inicio: start,
	                data_exercicio_final: end
	            }

	        }, file_type);
		}else Ext.Msg.show({
            msg: 'Selecione data início e data final',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        })
    },

    getEmployeeField: function(){
		if(!this._employeefield)
			this._employeefield = Ext._create('core.fields.AutocompleteField', {
                name: 'employee',
                rest: 'rh.employee.Restful',
                fieldLabel: 'Servidor',
                width: 350
			});

		return this._employeefield;
	},

	getJobPosition: function(){
		if(!this._jobposition)
			this._jobposition = Ext._create('core.fields.AutocompleteField', {
                name: 'jobposition',
                rest: 'rh.jobposition.Restful',
                fieldLabel: 'Cargo',
                width: 350
			});

		return this._jobposition;
	},

	getAtivo: function(){
        if(!this._ativo){
            this._ativo = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Ativo',
                hiddenName: 'ativo',
                ativo: 'ativo',
                width: 350,
                triggerAction: 'all',
                store: [
                    ['s', 'SIM'],
                    ['n', 'NÃO']
                ],
            });
        }

        return this._ativo;
    },

    getType: function(){
        if(!this._type){
            this._type = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Tipo',
                hiddenName: 'tipo',
                ativo: 'tipo',
                width: 350,
                triggerAction: 'all',
                store: [
                    ['EF', 'EFETIVO'],
				    ['CM', 'COMISSÃO'],
				    ['FC', 'FUNÇÃO DE CONFIANÇA'],
				    ['AC', 'ACORDO DE COOPERAÇÃO TÉCNICA'],
				    ['ES', 'ESTAGIÁRIO'],
				    ['EL', 'ELETIVO'],
				    ['TE', 'TERCEIRIZADO'],
				    ['VL', 'VOLUNTÁRIO']
                ],
            });
        }

        return this._type;
    },

    getEmployeeType: function(){
        if(!this._employeetype){
            this._employeetype = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Tipo do Servidor',
                hiddenName: 'tipo',
                ativo: 'tipo',
                width: 350,
                triggerAction: 'all',
                store: [
                    ['I', 'INDEFINIDO'],
				    ['E', 'ESTAGIÁRIO'],
				    ['M', 'MEMBRO DO MINISTÉRIO PÚBLICO'],
				    ['P', 'MILITAR'],
				    ['S', 'SERVIDOR'],
				    ['T', 'TERCEIRIZADO'],
				    ['V', 'VOLUNTÁRIO']
                ],
            });
        }

        return this._employeetype;
    },

    getDateExStart: function() {
        if (!this._dateexstart)
            this._dateexstart = Ext._create('Ext.form.DateField', {
                name: 'start_date',
                fieldLabel: "Data Exercício Início",
                hidden: false,
                width: 350,
            });
        return this._dateexstart;
    },

    getDateExEnd: function() {
        if (!this._dateexend)
            this._dateexend = Ext._create('Ext.form.DateField', {
                name: 'end_date',
                fieldLabel: "Data Exercício Final",
                hidden: false,
                width: 350,
            });
        return this._dateexend;
    },

    getSituation: function(cfg) {
        if(!this._situation)
            this._situation = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Situação',
                name: 'situation',
                hiddenName: 'situation',
                choiceId: 'rh.SITUACAO_FUNCIONAL',
                width: 350
            });

        return this._situation;
    },

	getEspecialidade: function(){
		if(!this._especialidade)
			this._especialidade = Ext._create('core.fields.AutocompleteField', {
                name: 'especialidade',
                rest: 'rh.parameters.EspecialidadeRestful',
                fieldLabel: 'Especialidade',
                width: 350
			});

		return this._especialidade;
	},

	getWorkplace: function(){
		if(!this._workplace)
			this._workplace = Ext._create('core.fields.AutocompleteField', {
                name: 'workplace',
                rest: 'rh.workplace.Restful',
                fieldLabel: 'Lotação/Designação',
                width: 350
			});

		return this._workplace;
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
	        	// title: 'Informações do Contra-Cheque',
	        	region: 'center',
	        	border: false,
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		title: 'Impressão da Listagem de Servidores',
	        		name: 'fieldServidor',
	        		width: 500,
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
	        			this.getEmployeeField(),
	        			this.getJobPosition(),
	        			this.getEspecialidade(),
	        			this.getWorkplace(),
	        			this.getAtivo(),
	        			this.getSituation(),
	        			this.getType(),
	        			this.getEmployeeType(),
	        			this.getDateExStart(),
	        			this.getDateExEnd(),
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
                        },
                    {
                    	xtype: 'displayfield',
                    	value: '* Deixe os campos em branco para selecionar Todos',
                    	hideLabel: true,
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
			   title: 'Relatório -> Listagem de Servidores'
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

		rh.gfp.reports.PayCheckManage.superclass.constructor.call(this, cfg);
	}
});