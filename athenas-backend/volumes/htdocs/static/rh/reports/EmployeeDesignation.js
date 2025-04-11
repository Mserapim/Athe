/**
 *
 **/

 Ext._define('rh.reports.EmployeeDesignation', {
	extend: 'toolkit.widget.TabPanel',

	_buildReport: function(type){

		var jobposition = this.getJobPosition().getValue() == "" ? 't' : this.getJobPosition().getValue();
		var employee = this.getEmployeeField().getValue() == "" ? 't' : this.getEmployeeField().getValue();
		var yes_to_all = this.getYesToAll().getValue() == "" ? '0' : this.getYesToAll().getValue();
		var efe = (this.getEfe().getValue() != '0' && this.getEfe().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var ecm = (this.getEcm().getValue() != '0' && this.getEcm().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var mbr = (this.getMbr().getValue() != '0' && this.getMbr().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var mel = (this.getMel().getValue() != '0' && this.getMel().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var mcm = (this.getMcm().getValue() != '0' && this.getMcm().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var mec = (this.getMec().getValue() != '0' && this.getMec().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var cms = (this.getCms().getValue() != '0' && this.getCms().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var req = (this.getReq().getValue() != '0' && this.getReq().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var rcm = (this.getRcm().getValue() != '0' && this.getRcm().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var est = (this.getEst().getValue() != '0' && this.getEst().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var vol = (this.getVol().getValue() != '0' && this.getVol().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var ctr = (this.getCtr().getValue() != '0' && this.getCtr().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var ext = (this.getExt().getValue() != '0' && this.getExt().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var rfc = (this.getRfc().getValue() != '0' && this.getRfc().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var efc = (this.getEfc().getValue() != '0' && this.getEfc().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var jca = (this.getJca().getValue() != '0' && this.getJca().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var xxx = (this.getXxx().getValue() != '0' && this.getXxx().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var mbr2 = (this.getMbr2().getValue() != '0' && this.getMbr2().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var mel2 = (this.getMel2().getValue() != '0' && this.getMel2().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var mcm2 = (this.getMcm2().getValue() != '0' && this.getMcm2().getValue() != '' || yes_to_all == '1') ? '1' : '0';
		var mec2 = (this.getMec2().getValue() != '0' && this.getMec2().getValue() != '' || yes_to_all == '1') ? '1' : '0';
				
		engine.mq.Report.request({
            report: '/mt/mpe/rh/servidor/servidores_files',
            waitMessage: 'Gerando relatório...',
            params: {
                outfile: 'relatorio_de_designacao',
                report_name: 'Relatório de Designações',
				cargo: jobposition,
				servidor: employee,
				todas_anot: yes_to_all,
				efe: efe,
				ecm: ecm,
				mbr: mbr,
				mel: mel,
				mcm: mcm,
				mec: mec,
				cms: cms,
				req: req,
				rcm: rcm,
				est: est,
				vol: vol,
				ctr: ctr,
				ext: ext,
				rfc: rfc,
				efc: efc,
				jca: jca,
				xxx: xxx,
				mbr2: mbr2,
				mel2: mel2,
				mcm2: mcm2,
				mec2: mec2,
            }
        }, type);
    },

	getYesToAll: function () {
        if (!this._yestoall) {
            this._yestoall = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Sim para todas opções abaixo',
                hiddenName: 'yes_to_all',
                name: 'yes_to_all',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._yestoall;
    },

	getEfe: function () {
        if (!this._efe) {
            this._efe = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'SERVIDOR EFETIVO',
                hiddenName: 'efe',
                name: 'efe',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._efe;
    },

	getEcm: function () {
        if (!this._ecm) {
            this._ecm = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'SERVIDOR EFETIVO E COMISSIONADO',
                hiddenName: 'ecm',
                name: 'ecm',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._ecm;
    },

	getMbr: function () {
        if (!this._mbr) {
            this._mbr = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'MEMBRO',
                hiddenName: 'mbr',
                name: 'mbr',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._mbr;
    },

	getMel: function () {
        if (!this._mel) {
            this._mel = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'MEMBRO COM CARGO ELETIVO',
                hiddenName: 'mel',
                name: 'mel',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._mel;
    },

	getMcm: function () {
        if (!this._mcm) {
            this._mcm = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'MEMBRO COM CARGO COMISSIONADO',
                hiddenName: 'mcm',
                name: 'mcm',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._mcm;
    },

	getMec: function () {
        if (!this._mec) {
            this._mec = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'MEMBRO COM CARGO ELETIVO E COMISSIONADO',
                hiddenName: 'mec',
                name: 'mec',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._mec;
    },

	getCms: function () {
        if (!this._cms) {
            this._cms = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'SERVIDOR COMISSIONADO',
                hiddenName: 'cms',
                name: 'cms',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._cms;
    },

	getReq: function () {
        if (!this._req) {
            this._req = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'SERVIDOR REQUISITADO',
                hiddenName: 'req',
                name: 'req',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._req;
    },

	getRcm: function () {
        if (!this._rcm) {
            this._rcm = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'SERVIDOR REQUISITADO COMISSIONADO',
                hiddenName: 'rcm',
                name: 'rcm',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._rcm;
    },

	getEst: function () {
        if (!this._est) {
            this._est = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'ESTAGIÁRIO',
                hiddenName: 'est',
                name: 'est',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._est;
    },

	getVol: function () {
        if (!this._vol) {
            this._vol = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'VOLUNTÁRIO',
                hiddenName: 'vol',
                name: 'vol',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._vol;
    },

	getCtr: function () {
        if (!this._ctr) {
            this._ctr = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'SERVIDOR CONTRATADO',
                hiddenName: 'ctr',
                name: 'ctr',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._ctr;
    },

	getExt: function () {
        if (!this._ext) {
            this._ext = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'EXTERNO SEM VÍNCULO',
                hiddenName: 'ext',
                name: 'ext',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._ext;
    },

	getRfc: function () {
        if (!this._rfc) {
            this._rfc = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'SERVIDOR REQUISITADO COM FUNÇÃO',
                hiddenName: 'rfc',
                name: 'rfc',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._rfc;
    },

	getEfc: function () {
        if (!this._efc) {
            this._efc = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'SERVIDOR EFETIVO COM FUNÇÃO',
                hiddenName: 'efc',
                name: 'efc',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._efc;
    },

	getJca: function () {
        if (!this._jca) {
            this._jca = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'JOVEM CIDADÃO - APRENDIZ',
                hiddenName: 'jca',
                name: 'jca',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._jca;
    },

	getXxx: function () {
        if (!this._xxx) {
            this._xxx = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'DESCONHECIDO',
                hiddenName: 'xxx',
                name: 'xxx',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._xxx;
    },

	getMbr2: function () {
        if (!this._mbr2) {
            this._mbr2 = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'MEMBRO DE 2ª ENTRÂNCIA',
                hiddenName: 'mbr2',
                name: 'mbr2',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._mbr2;
    },

	getMel2: function () {
        if (!this._mel2) {
            this._mel2 = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'MEMBRO DE 2ª ENTRÂNCIA COM CARGO ELETIVO',
                hiddenName: 'mel2',
                name: 'mel2',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._mel2;
    },

	getMcm2: function () {
        if (!this._mcm2) {
            this._mcm2 = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'MEMBRO DE 2ª ENTRÂNCIA COM CARGO COMISSIONADO',
                hiddenName: 'mcm2',
                name: 'mcm2',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._mcm2;
    },

	getMec2: function () {
        if (!this.mec2) {
            this.mec2 = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'MEMBRO DE 2ª ENTRÂNCIA COM CARGO ELETIVO E COMISSIONADO',
                hiddenName: 'mec2',
                name: 'mec2',
                width: 350,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this.mec2;
    },

	getEmployeeField: function () {
        if (!this._employeefield)
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
				autoScroll: true,
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		title: 'Relatorio de Designações',
	        		name: 'fieldServidor',
	        		width: "33%",
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
						this.getEmployeeField(),
						this.getJobPosition(),
						this.getYesToAll(),
						this.getEfe(),
						this.getEcm(),
						this.getMbr(),
						this.getMel(),
						this.getMcm(),
						this.getMec(),
						this.getCms(),
						this.getReq(),
						this.getRcm(),
						this.getEst(),
						this.getVol(),
						this.getCtr(),
						this.getExt(),
						this.getRfc(),
						this.getEfc(),
						this.getJca(),
						this.getXxx(),
						this.getMbr2(),
						this.getMel2(),
						this.getMcm2(),
						this.getMec2(),
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
			   title: 'Relatório -> Designações'
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

		rh.reports.EmployeeDesignation.superclass.constructor.call(this, cfg);
	}
});