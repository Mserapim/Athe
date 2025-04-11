/**
 *
 **/

Ext._define('rh.reports.FuncionalForm', {
    extend: 'toolkit.widget.TabPanel',

    _buildReport: function (paycheck) {

        if (this.getEmployeeField().getValue()) {
            var employee = this.getEmployeeField().getValue();

            selections = this.getMultiCheckbox().getSelectionModel().getSelections(),
            selected = selections.map(function (selection) {
                return selection.data.value;
            }).join(',').split(",");

            var yes_to_all = this.getYesToAll().getValue();
            var Endereco = (this.getEndereco().getValue() != 0 || yes_to_all == 1) ? 1 : this.getEndereco().getValue();
            var Dependente = (this.getDependente().getValue() != 0 || yes_to_all == 1) ? 1 : this.getDependente().getValue();
            var Geral = Boolean(selected.find(e => e === 'anot_geral')) ? 1 : 0;
            var Afastamento = Boolean(selected.find(e => e === 'anot_afastamento')) ? 1 : 0;
            var Ausência = Boolean(selected.find(e => e === 'anot_ausencia')) ? 1 : 0;
            var Carreira = Boolean(selected.find(e => e === 'anot_carreira')) ? 1 : 0;
            var Enquadramento = Boolean(selected.find(e => e === 'anot_enquadramento')) ? 1 : 0;
            var Elogio = Boolean(selected.find(e => e === 'anot_elogio')) ? 1 : 0;
            var Evento = Boolean(selected.find(e => e === 'anot_evento')) ? 1 : 0;
            var Falta = Boolean(selected.find(e => e === 'anot_falta')) ? 1 : 0;
            var Ferias = Boolean(selected.find(e => e === 'anot_ferias')) ? 1 : 0;
            var FolgaEleitoral = Boolean(selected.find(e => e === 'anot_folga_eleitoral')) ? 1 : 0;
            var Gratificacao = Boolean(selected.find(e => e === 'anot_gratificacao')) ? 1 : 0;
            var Licenca = Boolean(selected.find(e => e === 'anot_licenca')) ? 1 : 0;
            var PenaDisciplinar = Boolean(selected.find(e => e === 'anot_pena_disciplinar')) ? 1 : 0;
            var Plantao = Boolean(selected.find(e => e === 'anot_plantao')) ? 1 : 0;
            var Recesso = Boolean(selected.find(e => e === 'anot_recesso')) ? 1 : 0;
            var Remocao = Boolean(selected.find(e => e === 'anot_remocao')) ? 1 : 0;
            var TempoDobro = Boolean(selected.find(e => e === 'anot_tempo_dobro')) ? 1 : 0;
            var TempoServico = Boolean(selected.find(e => e === 'anot_tempo_servico')) ? 1 : 0;
            var Transposicao = Boolean(selected.find(e => e === 'anot_transposicao')) ? 1 : 0;
            var Viagem = Boolean(selected.find(e => e === 'anot_viagem')) ? 1 : 0;
            var storageDir = this.getStorageDir();

            engine.mq.Report.request({
                report: '/to/mpe/rh/servidor/ficha_funcional',
                waitMessage: 'Gerando relatório...',
                params: {

                    outfile: 'ficha_funcional',
                    report_name: 'Ficha Funcional - ' + this.getEmployeeField().getRawValue(),
                    servidor: employee,
                    todas_anot: yes_to_all,
                    endereco: Endereco,
                    dependente: Dependente,
                    anot_geral: Geral,
                    anot_afastamento: Afastamento,
                    anot_ausencia: Ausência,
                    anot_carreira: Carreira,
                    anot_enquadramento: Enquadramento,
                    anot_elogio: Elogio,
                    anot_evento: Evento,
                    anot_falta: Falta,
                    anot_ferias: Ferias,
                    anot_folga_eleitoral: FolgaEleitoral,
                    anot_gratificacao: Gratificacao,
                    anot_licenca: Licenca,
                    anot_pena_disciplinar: PenaDisciplinar,
                    anot_plantao: Plantao,
                    anot_recesso: Recesso,
                    anot_remocao: Remocao,
                    anot_tempo_dobro: TempoDobro,
                    anot_tempo_servico: TempoServico,
                    anot_transposicao: Transposicao,
                    anot_viagem: Viagem,
                    anot_aposentadoria: 0,
                    anot_promocao: 0,
                    upload_dir: storageDir
                }

            });
        } else Ext.Msg.show({
            msg: 'Selecione o Servidor',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        });

    },

    getMultiCheckbox: function () {
        if (!this._multiReportGrid) {
            var selectionModel = new Ext.grid.CheckboxSelectionModel({ checkOnly: true });
            this._multiReportGrid = Ext._create('Ext.grid.GridPanel', {
                fieldLabel: 'Tipos de Servidores',
                sm: selectionModel,
                deferRowRender: false,
                stripRows: true,
                style: { border: '0.5px solid #99bbe8' },
                columnLines: true,
                height: 250,
                anchor: '99%',
                autoExpandColumn: 'description',
                checked: true,
                store: Ext._create('Ext.data.Store', {
                    autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('RHFuncionalFormReport', 'get_annotations')
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            { name: 'value', type: 'string' },
                            { name: 'description', type: 'string' }
                        ]
                    })
                }),
                columns: [
                    selectionModel,
                    { header: 'Sigla', dataIndex: 'value', hidden: true, width: 50 },
                    { header: 'Tipos', dataIndex: 'description', id: 'description' },
                ],
                
            });
               
        }
        this._multiReportGrid.getStore().on({
            scope: this,
            load: function () {
                this.markAll(this._multiReportGrid);
            }
        });

        console.log(this._multiReportGrid)
        return this._multiReportGrid;
    },

    markAll: function (grid) {
        var _data = grid.getStore().data;
        var _selected = [];
        for (i = 0; i <= _data.length; i++) {
            _data.items.map(function (item) {
                    _selected.push(item)
            });
        }
        grid.getSelectionModel().clearSelections();
        grid.getSelectionModel().selectRecords(_selected);
    },

    getStorageDir: function () {
        return this.storageDir;
    },

    getEmployeeField: function () {
        if (!this._employeefield)
            this._employeefield = Ext._create('core.fields.AutocompleteField', {
                name: 'employee',
                rest: 'rh.employee.Restful',
                fieldLabel: 'Servidor',
                width: 450
            });

        return this._employeefield;
    },

    getYesToAll: function () {
        if (!this._yestoall) {
            this._yestoall = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Sim para todas opções abaixo',
                hiddenName: 'yes_to_all',
                name: 'yes_to_all',
                width: 450,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._yestoall;
    },

    getEndereco: function () {
        if (!this._endereco) {
            this._endereco = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Endereço',
                hiddenName: 'endereco',
                name: 'endereco',
                width: 450,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._endereco;
    },

    getDependente: function () {
        if (!this._dependente) {
            this._dependente = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Dependente',
                hiddenName: 'dependende',
                name: 'dependende',
                width: 450,
                triggerAction: 'all',
                store: [
                    [1, 'SIM'],
                    [0, 'NÃO']
                ],
            });
        }

        return this._dependente;
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
                        autoScroll: true,
                        items: [
                            {
                                xtype: 'fieldset',
                                title: 'Ficha Funcional',
                                name: 'fieldServidor',
                                width: "33%",
                                style: 'margin: 5px',
                                align: 'center',
                                items: [
                                    this.getEmployeeField(),
                                    // this.getYesToAll(),
                                    this.getEndereco(),
                                    this.getDependente(),
                                    this.getMultiCheckbox(),
                                    {
                                        xtype: 'button',
                                        iconCls: 'icon-siatu icon-siatu-move-down',
                                        style: 'margin-top: 10px',
                                        text: 'Gerar Relatório',
                                        width: 100,
                                        height: 25,
                                        scope: this,
                                        handler: this._buildReport,
                                    },
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
                title: 'Relatório -> Ficha Funcional'
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

        rh.reports.FuncionalForm.superclass.constructor.call(this, cfg);
    }
});