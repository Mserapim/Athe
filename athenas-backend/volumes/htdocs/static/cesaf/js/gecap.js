if(typeof(toolkit.cesaf.gecap) == 'undefined') {
    Ext.ns('toolkit.cesaf.gecap');

    toolkit.cesaf.gecap.CopyInvestimento = Ext.extend(
        Ext.Window,
        {
            getGridPanel: function() {
                if(!this.gridCache) {
                    var store = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            'GCAPGerenciador',
                            'get_store',
                            ['inscricao']
                        ),
                        baseParams: {
                            capacitacao: this.capacitacao
                        },
                        fields: ['codigo', 'status', 'nome', 'valor'],
                        root: 'result',
                        autoLoad: true,
                        listeners: {
                            scope: this,
                            load: function(store) {

                                store.filterBy(
                                    function(record) {
                                        return (this.to != record.get('codigo'));
                                    },
                                    this
                                );

                            }
                        }
                    });

                    this.gridCache = new Ext.grid.GridPanel({
                        region: 'center',
                        border: false,
                        cm: new Ext.grid.ColumnModel([
                            {
                                dataIndex: 'status',
                                width: 40,
                                sortable: false,
                                header: '',
                                id: 'status',
                                renderer: toolkit.util.formatStatus,
                                menuDisabled: true
                            },
                            {dataIndex: 'nome', width: 400, sortable: true, header: 'Nome'},
                            {dataIndex: 'valor', width: 70, sortable: true, header: 'Valor (R$)'}
                        ]),
                        store: store,
                        sm: new Ext.grid.RowSelectionModel({singleSelection: true}),
                        bbar: new Ext.PagingToolbar({
                            store: store
                        })
                    });
                }

                return this.gridCache;
            },

            copy: function() {
                var selection = this.getGridPanel().getSelectionModel();

                if(selection.getSelected()) {
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            'GCAPInvestimento',
                            'copy'
                        ),
                        params: {
                            from: selection.getSelected().get('codigo'),
                            to: this.to
                        },
                        success: function() {
                            this.trigger();
                            this.destroy();
                        },
                        fialure: function() {
                            alert('Ocorreu um problema tenando copiar os investimentos.');
                        },
                        scope: this
                    });
                }
            },

            constructor: function(to, capacitacao, trigger) {

                var cf = {
                    to: to,
                    capacitacao: capacitacao,
                    trigger: trigger,
                    title: 'Copiar investimentos',
                    closable: true,
                    resizable: true,
                    modal: true,
                    width: 550,
                    height: 300,
                    layout: 'border',
                    buttons: [
                        {
                            text: 'Copiar',
                            handler: this.copy,
                            scope: this
                        },
                        {
                            text: 'Cancelar',
                            scope: this,
                            handler: this.destroy
                        }
                    ]
                };

                toolkit.cesaf.gecap.CopyInvestimento.superclass.constructor.call(this, cf);

                this.add(this.getGridPanel());
            }
        }
    );

    toolkit.cesaf.gecap.GestorInvestimento = Ext.extend(
        Ext.Window,
        {
            addInvestimento: function() {
                var scope = this;

                new toolkit.cesaf.gecap.Investimento(
                    0,
                    0,
                    this.configuration.capacitacao.codigo,
                    null,
                    {},
                    function() {scope.refreshGrid();}
                ).show();
            },

            editInvestimento: function() {
                var scope = this;
                var selection = this.getGridInvestimento().getSelectionModel();

                if(selection.getSelected()) {
                    if(selection.getSelected().get('status')[0].alt == 'Grupo') {
                        new toolkit.cesaf.gecap.Investimento(
                            0,
                            1,
                            this.capacitacao,
                            null,
                            {
                                pk: selection.getSelected().get('pk'),
                                descricao: selection.getSelected().get('description'),
                                valor: selection.getSelected().get('valor')
                            },
                            function() {scope.refreshGrid();}
                        ).show();
                    }
                    else alert('Não posso manipular investimentos individuais.');
                }
                else alert('Primeiro selecione o investimento que deseja editar.');
            },



            deleteInvestimento: function() {
                var scope = this;
                var selection = this.getGridInvestimento().getSelectionModel();

                if(selection.getSelected()) {
                    Ext.Msg.show({
                        title: 'Removendo investimentos',
                        msg: 'Tem certeza que deseja remover os investimentos selecionados?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        fn: function(bnt) {
                            if(bnt != 'yes') return;

                            var fifo = [];
                            Ext.each(selection.getSelections(),function(record) {fifo.push(record.get('pk'));});

                            Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action(
                                    'GCAPInvestimento',
                                    'delete'
                                ),
                                params: {
                                    pk: fifo
                                },
                                success: function(request) {
                                    var result = Ext.decode(request.responseText);
                                    if(!result.success) alert('Ocorreu um erro tentando remover os investimentos.');
                                    this.refreshGrid();
                                },
                                scope: this
                            });
                        },
                        scope: this
                    });
                }
                else alert('Primeiro selecione o investimento que deseja editar.');
            },

            refreshGrid: function() {
                this.getGridInvestimento().getStore().reload();
            },

            getGridInvestimento: function() {
                if(!this.gridInvestimento) {
                    this.gridInvestimento = new Ext.grid.GridPanel({
                        region: 'center',
                        cm: new Ext.grid.ColumnModel([
                            {
                                id: 'status',
                                dataIndex: 'status',
                                header: '',
                                width: 25,
                                sortable: false,
                                renderer: toolkit.util.formatStatus,
                                menuDisabled: true
                            },
                            {dataIndex: 'description_ex', header: 'Descrição', width: 365, sortable: true},
                            {
                                dataIndex: 'valor',
                                header: 'Valor (R$)',
                                width: 70,
                                sortable: false,
                                renderer: function(valor) {
                                    return '<p style="text-align:right">' +
                                               Ext.util.Format.number(valor, '0.0,00/i') +
                                           '</p>';
                                }
                            }
                        ]),
                        store: new Ext.data.JsonStore({
                            url: toolkit.util.Normalize.controller_action(
                                'GCAPInvestimento',
                                'list'
                            ),
                            baseParams: {
                                capacitacao: this.configuration.capacitacao.codigo
                            },
                            root: 'result',
                            fields: ['status', 'description_ex', 'description', 'valor', 'pk'],
                            autoLoad: true,
                            listeners: {
                                scope: this,
                                load: function(store) {
                                    var total = {
                                        'Individual': 0.0,
                                        'Grupo': 0.0,
                                        'Geral': 0.0
                                    };

                                    store.each(function(record) {
                                        total[record.get('status')[0].alt] += eval(record.get('valor'));
                                        total.Geral += eval(record.get('valor'));
                                    });

                                    this.getGridInvestimento().getBottomToolbar().removeAll();
                                    this.getGridInvestimento().getBottomToolbar().add([
                                        '->',
                                        '-',
                                        'Participantes: R$ ' + Ext.util.Format.number(total.Individual, '0.0,00/i'),
                                        '-',
                                        'Grupo: R$ ' + Ext.util.Format.number(total.Grupo, '0.0,00/i'),
                                        '-',
                                        'Total: R$ ' + Ext.util.Format.number(total.Geral, '0.0,00/i')
                                    ]);
                                }
                            }
                        }),
                        tbar: [
                            {
                                text: 'Adicionar',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/add.png',
                                scope: this,
                                handler: this.addInvestimento
                            },
                            {
                                text: 'Editar',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/edit.png',
                                scope: this,
                                handler: this.editInvestimento
                            },
                            {
                                text: 'Excluir',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/delete.png',
                                scope: this,
                                handler: this.deleteInvestimento
                            }
                        ],
                        bbar: [
                            'Gasto com os participantes: R$ 0,00',
                            '-',
                            '->',
                            '-',
                            'Gasto total com o evento: R$ 0,00'
                        ]
                    });
                }

                return this.gridInvestimento;
            },

            getPanelInformation: function() {
                if(!this.panelInformation) {
                    var tpl = new Ext.XTemplate(
                        '<table style="padding:5pt">',
                            '<tr>',
                                '<td><p style="font-weight:bold;text-align:right">Tema : </p></td>',
                                '<td>',
                                    '<p style="padding: 2pt; padding-left: 20px; background: url({icon}) no-repeat">',
                                        '{tema}',
                                    '</p>',
                            '</tr>',
                            '<tr>',
                                '<td><p style="font-weight:bold;text-align:right">Realizado : </p></td>',
                                '<td>',
                                    '<p style="padding: 2pt">',
                                        'De {dt_inicio} até {dt_fim} com a carga horária de {carga_hora}ora(s)',
                                    '</p>',
                            '</tr>',
                            '<tr>',
                                '<td><p style="font-weight:bold;text-align:right">Cidade : </p></td>',
                                '<td>',
                                    '<p style="padding: 2pt">',
                                        '{cidade}',
                                    '</p>',
                            '</tr>',
                        '</table>'
                    );

                    var cf = {
                        tema: this.configuration.capacitacao.nome,
                        icon: '/' + global.Context + '/' + this.configuration.capacitacao.status.icon,
                        dt_inicio: this.configuration.capacitacao.dt_inicio,
                        dt_fim: this.configuration.capacitacao.dt_fim,
                        cidade: this.configuration.capacitacao.cidade,
                        carga_hora: this.configuration.capacitacao.carga_horaria
                    };

                    this.panelInformation = new Ext.Panel({
                        region: 'north',
                        maxHeight: 75,
                        minHeight: 75,
                        height: 75,
                        split: true,
                        border: true,
                        html: tpl.apply(cf)
                    });
                }

                return this.panelInformation;
            },

            constructor: function(capacitacao, trigger) {
                var cf = {
                    title: 'Gestor de Investimentos em Capacitação',
                    width: 500,
                    height: 400,
                    closable: true,
                    resizable: false,
                    border: false,
                    layout: 'border',
                    modal: true,
                    configuration: {
                        capacitacao: capacitacao,
                        trigger: trigger
                    }
                };

                toolkit.cesaf.gecap.GestorInvestimento.superclass.constructor.call(this, cf);

                this.add(this.getPanelInformation());
                this.add(this.getGridInvestimento());
            }
        }
    );

    toolkit.cesaf.gecap.Investimento = Ext.extend(
        Ext.Window,
        {
            TYPE: {
                CAPACITACAO: 0,
                CAPACITANDO: 1
            },

            ACTION: {
                ADD: 0,
                EDIT: 1
            },

            constructor: function(type, action, capacitacao, inscricao, values, trigger) {

                var cf = {
                    title: 'Investimento',
                    closable: true,
                    resizable: false,
                    modal: true,
                    border: false,
                    width: 500,
                    configuration: {
                        type: type,
                        action: action,
                        capacitacao: capacitacao,
                        inscricao: inscricao,
                        values: values,
                        trigger: trigger
                    },
                    buttons: [
                        {
                            text: 'Salvar',
                            scope: this,
                            handler: this.commit
                        },
                        {
                            text: 'Cancelar',
                            scope: this,
                            handler: this.destroy
                        }
                    ]
                };

                toolkit.cesaf.gecap.Investimento.superclass.constructor.call(this, cf);

                this.add(this.getFormPanel());
            },

            commit: function() {
                var form = this.getFormPanel().getForm();
                form.waitMsgTarget = this.getEl();
                form.submit({
                    waitMsg: 'Gravando dados do investimento',
                    url: toolkit.util.Normalize.controller_action(
                        'GCAPInvestimento',
                        this.configuration.action == 0 ? 'add': 'update'
                    ),
                    params: {
                        pk: this.configuration.values.pk,
                        capacitacao: this.configuration.capacitacao,
                        inscricao: this.configuration.inscricao
                    },
                    validate: 'client',
                    success: function() {
                        this.configuration.trigger();
                        this.destroy();
                    },
                    failure: function() {
                        alert('Não foi possivel gravar informações do investimento.');
                    },
                    scope: this
                });
            },

            getFormPanel: function() {
                if(!this.formPanel) {
                    this.formPanel = new Ext.form.FormPanel({
                        frame: true,
                        defaults: {
                            width: 365
                        },
                        items: [
                            {
                                xtype: 'textfield',
                                fieldLabel: 'Descrição',
                                name: 'descricao',
                                allowBlank: false,
                                value: this.configuration.values.descricao
                            },
                            {
                                xtype: 'numberfield',
                                fieldLabel: 'Valor (R$)',
                                name: 'valor',
                                allowBlank: false,
                                value: this.configuration.values.valor
                            }
                        ]
                    });
                }

                return this.formPanel;
            }
        }
    );

    toolkit.cesaf.gecap.Inscricao = Ext.extend(
        Ext.Window,
        {
            getInscricao: function() {return this.inscricao;},

            setInscricao: function(pk) {
                this.inscricao = pk;

                if(this.inscricao) {
                    this.getFormPanel().getForm().findField('servidor').disable();
                    this.refreshGridInvestimento();
                    this.getGridInvestimento().getTopToolbar().items.each(function(bnt) {bnt.enable();});
                }
                else{
                    this.getGridInvestimento().getTopToolbar().items.each(function(bnt) {bnt.disable();});
                }
            },

            refreshGridInvestimento: function() {
                var store = this.getGridInvestimento().getStore();
                var total = 0.0;

                store.baseParams = {
                    capacitacao: this.capacitacao,
                    inscricao: this.getInscricao()
                };

                store.reload();

                /*
                 * Recarrega o grid para atualizar o valor, deve ser modificado para gatilho.
                 */
                this.store.reload();
            },

            addInvestimento: function() {
                var scope = this;

                new toolkit.cesaf.gecap.Investimento(
                    0,
                    0,
                    this.capacitacao,
                    this.getInscricao(),
                    {},
                    function() {scope.refreshGridInvestimento();}
                ).show();
            },

            editInvestimento: function() {
                var scope = this;
                var selection = this.getGridInvestimento().getSelectionModel();

                if(selection.getSelected()) {
                    new toolkit.cesaf.gecap.Investimento(
                        0,
                        1,
                        this.capacitacao,
                        this.getInscricao(),
                        {
                            pk: selection.getSelected().get('pk'),
                            descricao: selection.getSelected().get('description'),
                            valor: selection.getSelected().get('valor')
                        },
                        function() {scope.refreshGridInvestimento();}
                    ).show();
                }
                else alert('Primeiro selecione o investimento que deseja editar.');
            },

            copyInvestimento: function() {
                var scope = this;

                new toolkit.cesaf.gecap.CopyInvestimento(
                    this.getInscricao(),
                    this.capacitacao,
                    function() { scope.refreshGridInvestimento(); }
                ).show();
            },

            deleteInvestimento: function() {
                var scope = this;
                var selection = this.getGridInvestimento().getSelectionModel();

                if(selection.getSelected()) {
                    Ext.Msg.show({
                        title: 'Removendo investimentos',
                        msg: 'Tem certeza que deseja remover os investimentos selecionados?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        fn: function(bnt) {
                            if(bnt != 'yes') return;

                            var fifo = [];
                            Ext.each(selection.getSelections(),function(record) {fifo.push(record.get('pk'));});

                            Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action(
                                    'GCAPInvestimento',
                                    'delete'
                                ),
                                params: {
                                    pk: fifo
                                },
                                success: function(request) {
                                    var result = Ext.decode(request.responseText);
                                    if(!result.success) alert('Ocorreu um erro tentando remover os investimentos.');
                                    this.refreshGridInvestimento();
                                },
                                scope: this
                            });
                        },
                        scope: this
                    });
                }
                else alert('Primeiro selecione o investimento que deseja editar.');
            },

            getGridInvestimento: function() {
                if(!this.gridInvestimento) {
                    this.gridInvestimento = new Ext.grid.GridPanel({
                        tbar: [
                            {
                                icon: '/' + global.Context + '/static/images/add.png',
                                iconCls: true,
                                text: 'Nova inscrição',
                                disabled: true,
                                handler: function(){
                                    this.setInscricao(undefined);
                                    this.getFormPanel().getForm().findField('servidor').enable();
                                    this.getFormPanel().getForm().findField('servidor').clearValue();
                                    this.getStoreInvestimento().baseParams = {
                                        capacitacao: this.capacitacao,
                                        inscricao: this.getInscricao()
                                    };
                                    this.getStoreInvestimento().reload();
                                },
                                scope: this,
                                tooltip: 'Nova inscrição'
                            },
                            '-',
                            {
                                icon: '/' + global.Context + '/static/images/add.png',
                                iconCls: true,
                                text: 'Adicionar',
                                disabled: true,
                                handler: this.addInvestimento,
                                scope: this,
                                tooltip: 'Adicionar um novo investimento'
                            },
                            {
                                icon: '/' + global.Context + '/static/images/edit.png',
                                iconCls: true,
                                text: 'Editar',
                                disabled: true,
                                handler: this.editInvestimento,
                                scope: this,
                                tooltip: 'Editar um investimento'
                            },
                            {
                                icon: '/' + global.Context + '/static/images/delete.png',
                                iconCls: true,
                                text: 'Excluir',
                                disabled: true,
                                scope: this,
                                tooltip: 'Excluir um investimento',
                                handler: this.deleteInvestimento
                            },
                            '-',
                            {
                                text: 'Copiar de',
                                icon: '/' + global.Context + '/static/cesaf/images/copy.png',
                                iconCls: true,
                                disabled: true,
                                tooltip: 'Copiar investimentos de outra inscrição.',
                                scope: this,
                                handler: this.copyInvestimento
                            }
                        ],
                        listeners: {
                            scope: this,
                            dblclick: function() {
                                this.editInvestimento();
                            }
                        },
                        bbar: [
                            '->',
                            {
                                xtype: 'tbtext',
                                text: 'Total R$ 0,00'
                            }
                        ],
                        border: false,
                        cm: new Ext.grid.ColumnModel([
                            {header: 'Item', dataIndex: 'item', sortable: true, width: 50},
                            {header: 'Descrição', dataIndex: 'description', sortable: true, width: 350},
                            {
                                header: 'Valor (R$)',
                                dataIndex: 'valor',
                                sortable: true,
                                width: 100,
                                renderer: function(valor) {
                                    return  '<p style="text-align:right">' +
                                                Ext.util.Format.number(valor, '0.0,00/i') +
                                            '</p>';
                                }
                            },
                        ]),
                        height: 220,
                        store: this.getStoreInvestimento()
                    });
                }

                return this.gridInvestimento;
            },

            getStoreInvestimento: function(){
                if(!this.storeInvestimento){
                    this.storeInvestimento = new Ext.data.JsonStore({
                        fields: ['item', 'description', 'valor', 'pk'],
                        root: 'result',
                        url: toolkit.util.Normalize.controller_action(
                            'GCAPInvestimento',
                            'list'
                        ),
                        listeners: {
                            scope: this,
                            load: function(store) {
                                var total = 0.0;
                                var bbar = this.getGridInvestimento().getBottomToolbar();

                                store.each(function(record) {total += eval(record.get('valor'));});

                                bbar.removeAll();
                                bbar.add('->');
                                bbar.add('Total (R$): ' + Ext.util.Format.number(total, '0.0,00/i'));
                            }
                        }
                    });
                }
                return this.storeInvestimento;
            },

            getFormPanel: function() {
                if(!this.formPanel) {
                    this.formPanel = new Ext.form.FormPanel({
                        frame: true,
                        border: false,
                        defaults: {
                            width: '420',
                            labelWidth: 50,
                        },
                        items: [
                            {
                                xtype: 'rest-autocompletefield',
                                fieldLabel: "Servidor",
                                allowBlank: false,
                                rest: "rh.employee.Restful",
                                name: "servidor",
                                gridConfig: {
                                    configOrderToolBar: ['search', '->'],
                                    columnAction: false,
                                    hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode']
                                },
                                value: this.values.servidor,
                            },
                            {
                                name: 'certificado',
                                fieldLabel: 'Certificado',
                                xtype: 'ged-fileuploadfield',
                                value: this.values.certificado,
                            }
                        ]
                    });
                }

                return this.formPanel;
            },

            commit: function() {
                this.getFormPanel().getForm().waitMsgTarget = this.getEl();

                this.getFormPanel().getForm().submit({
                    scope: this,
                    waitMsg: 'Gravando os dados da inscrição.',
                    url: toolkit.util.Normalize.controller_action(
                        'GCAPInscricao',
                        this.getInscricao() ? 'update': 'add'
                    ),
                    params: {
                        capacitacao: this.capacitacao,
                        pk: this.getInscricao()
                    },
                    success: function(form, action) {this.setInscricao(action.result.pk);this.store.reload();},
                    failure: function() {alert('Ocorreu um erro tentando gravar os dados da inscrição.');}
                });
            },

            constructor: function(capacitacao, store, values) {

                this.buttonCommit = new Ext.Button({
                        text: 'Salvar',
                        scope: this,
                        handler: this.commit
                    }
                );

                var cf = {
                    title: 'Inscrição',
                    closable: true,
                    width: 550,
                    height: 350,
                    modal: true,
                    resizable: true,
                    capacitacao: capacitacao,
                    store: store,
                    values: values ? values : {},
                    buttons: [
                        this.buttonCommit,
                        {
                            text: 'Fechar',
                            scope: this,
                            handler: this.destroy
                        },
                    ]
                };

                toolkit.cesaf.gecap.Inscricao.superclass.constructor.call(this, cf);
                this.add(this.getFormPanel());
                this.add(this.getGridInvestimento());
                this.setInscricao(this.values.inscricao);
            }
        }
    );

    toolkit.cesaf.gecap.Gerenciador = Ext.extend(
        Ext.Panel,
        {

            _not_implemented: function(){
                console.debug("not implemented");
            },

            constructor: function(args) {
                var cf = {
                    title: 'Capacitação',
                    closable: true,
                    layout: {
                        type:'vbox',
                        padding:'5',
                        align:'stretch'
                    },
                    defaults:{margins:'0 0 5 0'}

                };

                toolkit.cesaf.gecap.Gerenciador.superclass.constructor.call(this, cf);

                var active = toolkit.Application.tabspace.getActiveTab();
                toolkit.Application.tabspace.remove(active);
                toolkit.Application.tabspace.add(this);

                this.add(this.getPanelCapacitacao());
                this.add(this.getPanelPartInscricao());

                var obj = this;
                setTimeout(function() {
                    obj.doLayout();
                }, 50);

                this.on(
                    'render',
                    function() {
                        this.getStoreGridCapacitacao().load({
                            params:{
                                start: 0,
                                limit: 50
                            }
                        });
                    },
                    this
                );
            },

            /*****
             *
             *    PANEL CAPACITACAO
             *
             **/
            getPanelCapacitacao: function(){
                if(!this.panelCapacitacao){
                    this.panelCapacitacao = new Ext.grid.GridPanel({
                        title: "<b>Capacitação</b>",
                        cm: this.getCapacitacaoColumnModel(),
                        store: this.getStoreGridCapacitacao(),
                        border: true,
                        flex: 1,
                        sm: new Ext.grid.RowSelectionModel({
                            singleSelect:false,
                             listeners: {
                                 scope: this,
                                 rowselect: function(sm) {
                                    this.getStoreGridPartInscricao().baseParams.capacitacao = sm.getSelected().get('codigo');
                                    this.getStoreGridPartInscricao().load({params:{start:0, limit:50}});
                                 }
                             }
                        }),
                        bbar: this.getCapacitacaoGridPaginator(),
                        tbar: this.getCapacitacaoGridToolbar(),
                         listeners: {
                             scope: this,
                             dblclick: function() {
                                if(this.panelCapacitacao.getSelectionModel().getSelected()){
                                    new toolkit.widget.ExtCrudForm(
                                        this.getFatherCapacitacao(this.panelCapacitacao.getSelectionModel().getSelected().get('tipo')),
                                        toolkit.widget.ExtCrudForm.TYPE.EDIT,
                                        this.panelCapacitacao.getSelectionModel().getSelected().get('codigo')
                                    ).show();
                                }
                             }
                         }
                    });
                }
                return this.panelCapacitacao;
            },

            getFatherCapacitacao: function(tipo) {
                var father = false;

                var dict = {
                    'curso': 'GCAPCurso',
                    'congresso': 'GCAPCongresso',
                    'feira': 'GCAPFeira',
                    'oficina': 'GCAPOficina',
                    'reuniao': 'GCAPReuniao',
                    'seminario': 'GCAPSeminario',
                    'evento': 'GCAPEvento'
                };

                father = {
                    store: this.getStoreGridCapacitacao(),
                    controller: dict[tipo],
                    reload_grid: function(){
                        this.store.reload();
                    }
                };

                return father;
            },

            getStoreGridCapacitacao: function() {
                if(!this.storeGridCapacitacao) {
                    this.storeGridCapacitacao = new Ext.data.JsonStore({
                        fields: [
                            "codigo",
                            "nome",
                            "dt_inicio",
                            "dt_fim",
                            "carga_horaria",
                            "tipo",
                            "investimento",
                            "status",
                            "cidade"
                        ],
                        root: "result",
                        totalProperty: "totalRows",
                        url: toolkit.util.Normalize.controller_action(
                            "GCAPGerenciador",
                            "get_store",
                            ["capacitacao"]
                        ),
                        remoteSort: true
                    });
                }
                return this.storeGridCapacitacao;
            },

            getCapacitacaoColumnModel: function() {
                if(!this.capacitacaoColumnModel) {
                    this.capacitacaoColumnModel = new Ext.grid.ColumnModel([
                        {
                            id: 'status',
                            dataIndex: "status",
                            header: "",
                            menuDisabled: true,
                            sortable: false,
                            width: 25,
                            renderer: toolkit.util.formatStatus
                        },
                        {dataIndex: 'nome', header: 'Tema', sortable: true, width: 300},
                        {dataIndex: 'dt_inicio', header: 'Dt. Início', sortable: true, width: 100},
                        {dataIndex: 'dt_fim', header: 'Dt. Fim', sortable: true, width: 100},
                        {dataIndex: 'carga_horaria', header: 'C. Horária', sortable: false, width: 100},
                        {
                            dataIndex: 'investimento',
                            header: 'Investimento (R$)',
                            sortable: true,
                            width: 100,
                            renderer: function(value) {
                                return '<p style="text-align:right">' +
                                            Ext.util.Format.number(eval(value), '0.0,00/i') +
                                       '</p>';
                            }
                        }
                    ]);
                }
                return this.capacitacaoColumnModel;
            },

            getCapacitacaoGridPaginator: function() {
                if(!this.gridPaginator) {
                    this.gridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStoreGridCapacitacao(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    });
                }
                return this.gridPaginator;
            },

            addCapacitacao: function(type) {
                new toolkit.widget.ExtCrudForm(
                    this.getFatherCapacitacao(type),
                    toolkit.widget.ExtCrudForm.TYPE.NEW,
                    false,
                    []
                ).show();
            },

            editCapacitacao: function() {
                if(this.panelCapacitacao.getSelectionModel().getSelected()){
                    new toolkit.widget.ExtCrudForm(
                        this.getFatherCapacitacao(this.panelCapacitacao.getSelectionModel().getSelected().get('tipo')),
                        toolkit.widget.ExtCrudForm.TYPE.EDIT,
                        this.panelCapacitacao.getSelectionModel().getSelected().get('codigo')
                    ).show();
                }
                else alert('Primeiro selecione uma capacitação para edição.');
            },

            deleteCapacitacao: function(record) {
                var controller = this.getFatherCapacitacao(record.get('tipo')).controller;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action(
                        controller,
                        "commit",
                        ["DELETE", record.get("codigo"), 0]
                    ),
                    method: 'POST',
                    success: function() {
                        this.getStoreGridCapacitacao().reload();
                    },
                    scope: this
                });
            },

            deleteCapacitacoes: function() {
                if(this.panelCapacitacao.getSelectionModel().getSelections()){
                    var items = this.panelCapacitacao.getSelectionModel().getSelections();
                    Ext.Msg.show({
                        title:'Apagar itens selecionados?',
                        msg: 'Deseja apagar os itens selecionados?',
                        buttons: Ext.Msg.YESNO,
                        fn: function(b) {if(b == "yes") Ext.each(items, this.deleteCapacitacao, this);},
                        icon: Ext.MessageBox.QUESTION,
                        scope: this
                    });
                }
                else alert("É necessário selecionar o(s) item(ns)!");
            },

            openInvestimento: function() {
                var selection = this.getPanelCapacitacao().getSelectionModel();
                if(selection.getSelected()) {
                    new toolkit.cesaf.gecap.GestorInvestimento(
                        selection.getSelected().json,
                        this.getPanelCapacitacao().reload
                    ).show();
                }
                else alert('Para manipular investimento é necessário primeiro selecionar uma capacitação.');
            },

            requestCertificate: function() {
                var selection = this.getPanelCapacitacao().getSelectionModel();

                if(selection.getSelected()) {
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            'GCAPGerenciador',
                            'request_certificate'
                        ),
                        params: {
                            capacitacao: selection.getSelected().get('codigo')
                        },
                        success: function() {
                            alert('Notificações enviadas com sucesso.');
                        },
                        failure: function() {
                            alert('Não obtive sucesso no envio das notificações.');
                        }
                    });
                }
                else alert('Para solicitar os certificados, primeiro selecione uma capacitação.');
            },

            openResume: function() {
                var selection = this.getPanelCapacitacao().getSelectionModel().getSelected();
                if (selection){

                    engine.mq.Report.request({

                        report: '/to/mpe/cesaf/gecap/capacitacao_detalhado',

                        el: this.getEl(),

                        waitMessage: 'Gerando relatório...',

                        params: {

                            outfile: 'relatorio-investimento-geral-detalhado-' + selection.get('nome'),

                            report_name: 'Resumo da Capacitação - ' + selection.get('nome'),

                            gecap_id: selection.get('codigo'),

                        }

                    });

                }else{

                    Ext.Msg.show({

                        'title': 'Atenção',

                        'icon': Ext.Msg.INFO,

                        'buttons': Ext.Msg.OK,

                        'msg': 'Selecione pelo menos um item.'

                    });

                }
            },


            getCapacitacaoGridToolbar: function() {
                var menu = [];
                menu.push({
                    text: "Capacitação",
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/add.png",
                    scope: this,
                    menu:[
                        {
                            text: "Congresso",
                            iconCls: true,
                            icon: "/" + global.Context + "/static/cesaf/images/congresso.png",
                            handler: function(){this.addCapacitacao('congresso');},
                            scope: this
                        },
                        {
                            text: "Curso",
                            iconCls: true,
                            icon: "/" + global.Context + "/static/cesaf/images/curso.png",
                            handler: function(){this.addCapacitacao('curso');},
                            scope: this
                        },
                        {
                            text: "Feira",
                            iconCls: true,
                            icon: "/" + global.Context + "/static/cesaf/images/feira.png",
                            handler: function(){this.addCapacitacao('feira');},
                            scope: this
                        },
                        {
                            text: "Oficina",
                            iconCls: true,
                            icon: "/" + global.Context + "/static/cesaf/images/oficina.png",
                            handler: function(){this.addCapacitacao('oficina');},
                            scope: this
                        },
                        {
                            text: "Reunião",
                            iconCls: true,
                            icon: "/" + global.Context + "/static/cesaf/images/reuniao.png",
                            handler: function(){this.addCapacitacao('reuniao');},
                            scope: this
                        },
                        {
                            text: "Seminário",
                            iconCls: true,
                            icon: "/" + global.Context + "/static/cesaf/images/seminario.png",
                            handler: function(){this.addCapacitacao('seminario');},
                            scope: this
                        },
                        '-',
                        {
                            text: "Evento",
                            iconCls: true,
                            icon: "/" + global.Context + "/static/cesaf/images/evento.png",
                            handler: function(){this.addCapacitacao('evento');},
                            scope: this
                        }
                    ]
                });
                menu.push({
                    text: "Editar",
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/edit.png",
                    handler: this.editCapacitacao,
                    scope: this
                });
                menu.push({
                    text: "Excluir",
                    iconCls: true,
                    icon: "/" + global.Context + "/static/images/delete.png",
                    handler: this.deleteCapacitacoes,
                    scope: this
                });
                menu.push("-");
                menu.push({
                    text: "Investimento",
                    iconCls: true,
                    icon: "/" + global.Context + "/static/cesaf/images/investimento.png",
                    scope: this,
                    handler: this.openInvestimento
                });
                menu.push("-");
                menu.push({
                    text: "Certificado",
                    iconCls: true,
                    icon: "/" + global.Context + "/static/cesaf/images/certificado.png",
                    scope: this,
                    handler: this.requestCertificate
                });
                menu.push("-");
                menu.push({
                    text: "Relatórios",
                    iconCls: true,
                    icon: "/" + global.Context + "/static/cesaf/images/pdf.png",
                    menu: [
                        {
                            text: 'Resumo da Capacitação',
                            scope: this,
                            handler: this.openResume
                        }
                    ]
                });
                menu.push("-");
                menu.push("Busca:");
                menu.push({
                    xtype: "textfield",
                    emptyText: "Localizar uma capacitação",
                    width: 250,
                    listeners: {
                        scope: this,
                        change: function(field, new_value) {
                            var store = this.getPanelCapacitacao().getStore();

                            store.baseParams = {
                                start: 0,
                                limit: 50,
                                query: new_value
                            };

                            store.load({});
                        }
                    }
                });
                return menu;
            },

            /*****
             *
             *    PANEL PARTICIPANTES E INVESTIMENTO
             *
             **/
            getPanelPartInscricao: function(){
                if(!this.panelPartInscricao){
                    var father_inscricao = {
                        store: this.getStoreGridPartInscricao(),
                        controller: "GCAPInscricao",
                        reload_grid: function(){
                            this.store.reload();
                        }
                    };
                    this.panelPartInscricao = new Ext.grid.GridPanel({
                        title: "<b>Inscrição(ões) de Participante(s)</b>",
                        store: this.getStoreGridPartInscricao(),
                        cm: this.getPartInscricaoColumnModel(),
                        border: true,
                        flex: 1,
                        sm: new Ext.grid.RowSelectionModel({singleSelect:false}),
                        bbar: this.getPartInscricaoGridPaginator(),
                        tbar: this.getPartInscricaoGridToolbar(),
                        listeners: {
                            scope: this,
                            dblclick: this.editInscricao
                        }
                    });
                }
                return this.panelPartInscricao;
            },

            getStoreGridPartInscricao: function() {
                if(!this.storeGridPartInscricao) {
                    this.storeGridPartInscricao = new Ext.data.JsonStore({
                        fields: [
                            "codigo",
                            "status",
                            "nome",
                            "dt_cadastro",
                            'servidor',
                            'capacitacao',
                            'investimento'
                        ],
                        root: "result",
                        totalProperty: "totalRows",
                        url: toolkit.util.Normalize.controller_action(
                            "GCAPGerenciador",
                            "get_store",
                            ["inscricao"]
                        ),
                        baseParams:{
                            capacitacao: "",
                            start:0,
                            limit:50
                        },
                        remoteSort: true
                    });
                }
                return this.storeGridPartInscricao;
            },

            getPartInscricaoColumnModel: function() {
                if(!this.PartInscricaoColumnModel) {
                    this.PartInscricaoColumnModel = new Ext.grid.ColumnModel([
                        {
                            id:'status',
                            dataIndex: 'status',
                            header: '',
                            menuDisabled: true,
                            sortable: false,
                            width: 40,
                            renderer: toolkit.util.formatStatus
                        },
                        {dataIndex: 'nome', header: 'Nome', sortable: true, width: 300},
                        {dataIndex: 'dt_cadastro', header: 'Dt. Inscrição', sortable: true, width: 100},
                        {
                            dataIndex: 'investimento',
                            header: 'Investimento (R$)',
                            sortable: true,
                            width: 100,
                            renderer: function(value) {
                                return '<p style="text-align:right">' +
                                            Ext.util.Format.number(eval(value), '0.0,00/i') +
                                       '</p>';
                            }
                        },
                    ]);
                }
                return this.PartInscricaoColumnModel;
            },

            getPartInscricaoGridPaginator: function() {
                if(!this.partInscricaoGridPaginator) {
                    this.partInscricaoGridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStoreGridPartInscricao(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    });
                }

                return this.partInscricaoGridPaginator;
            },

            getFatherInscricao: function() {
                return {
                    store: this.getStoreGridPartInscricao(),
                    controller: "GCAPInscricao",
                    reload_grid: function(){
                        this.store.reload();
                    }
                };
            },

            addInscricao: function() {
                if(this.panelCapacitacao.getSelectionModel().getSelected()) {
                    new toolkit.cesaf.gecap.Inscricao(
                        this.panelCapacitacao.getSelectionModel().getSelected().get('codigo'),
                        this.getStoreGridPartInscricao()
                    ).show();
                }
                else alert("Escolha uma capacitação!");
            },

            editInscricao: function() {
                var selected = this.panelCapacitacao.getSelectionModel().getSelected();
                var iSelected = this.getPanelPartInscricao().getSelectionModel().getSelected();

                if(selected && iSelected) {
                    new toolkit.cesaf.gecap.Inscricao(
                        selected.get('codigo'),
                        this.getStoreGridPartInscricao(),
                        {
                            inscricao: iSelected.json.codigo,
                            servidor: iSelected.json.servidor,
                            certificado: iSelected.json.certificado
                        }
                    ).show();
                }
                else alert("Escolha uma inscrição!");
            },

            deleteInscricoes: function() {
                var selection = this.panelPartInscricao.getSelectionModel();

                if(selection.getSelections()) {
                    Ext.Msg.show({
                        title: 'Excluir as inscrições',
                        msg: 'Tem certeza que deseja excluir as incrições selecionadas?',
                        buttons: Ext.Msg.YESNO,
                        fn: function(bnt) {
                            var ic = [];

                            if(bnt == 'yes') {
                                Ext.each(
                                    selection.getSelections(),
                                    function(record) {ic.push(record.get('codigo'));}
                                );

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'GCAPInscricao',
                                        'delete'
                                    ),
                                    params: {
                                        inscricao: ic
                                    },
                                    success: function(request) {
                                        var result = Ext.decode(request.responseText);
                                        this.getStoreGridPartInscricao().reload();
                                    },
                                    failure: function() {
                                        alert('Ocorreu um erro tentando excluir as incrições selecionadas.');
                                    },
                                    scope: this
                                });
                            }
                        },
                        icon: Ext.Msg.QUESTION,
                        scope: this
                    });
                }
                else alert('Primeiro você deve selecionar as incrições que deseja excluir.');
            },

            homologarInscricoes: function() {
                var selection = this.panelPartInscricao.getSelectionModel();

                if(selection.getSelections()) {
                    Ext.Msg.show({
                        title: 'Homologar inscrições',
                        msg: 'Tem certeza que deseja homologar as incrições selecionadas?',
                        buttons: Ext.Msg.YESNO,
                        fn: function(bnt) {
                            var ic = [];

                            if(bnt == 'yes') {
                                Ext.each(
                                    selection.getSelections(),
                                    function(record) {ic.push(record.get('codigo'));}
                                );

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'GCAPInscricao',
                                        'homologar'
                                    ),
                                    params: {
                                        inscricao: ic
                                    },
                                    success: function(request) {
                                        var result = Ext.decode(request.responseText);
                                        this.getStoreGridPartInscricao().reload();
                                    },
                                    failure: function() {
                                        alert('Ocorreu um erro tentando homologar as incrições selecionadas.\nTente novamente mais tarde.');
                                    },
                                    scope: this
                                });
                            }
                        },
                        icon: Ext.Msg.QUESTION,
                        scope: this
                    });
                }
                else alert('Primeiro você deve selecionar as incrições que deseja homologar.');

            },

            getPartInscricaoGridToolbar: function() {
                if(!this.inscricaoToolbar) {
                    this.inscricaoToolbar = new Ext.Toolbar({
                        items: [
                            {
                                text: "Inscrição",
                                iconCls: true,
                                icon: "/" + global.Context + "/static/images/add.png",
                                scope: this,
                                handler: this.addInscricao
                            },
                            {
                                text: "Editar",
                                iconCls: true,
                                icon: "/" + global.Context + "/static/images/edit.png",
                                scope: this,
                                handler: this.editInscricao
                            },
                            {
                                text: "Excluir",
                                iconCls: true,
                                icon: "/" + global.Context + "/static/images/delete.png",
                                scope: this,
                                handler: this.deleteInscricoes
                            },
                            '-',
                            {
                                text: 'Homologar',
                                iconCls: true,
                                icon: "/" + global.Context + "/static/cesaf/images/homologar.png",
                                scope: this,
                                handler: this.homologarInscricoes
                            },
                            '-',
                            ' ',
                            'Buscar : ',
                            ' ',
                            {
                                xtype: "textfield",
                                width: 250,
                                emptyText: 'Localizar inscrição',
                                listeners: {
                                    scope: this,
                                    change: function(field, new_value) {
                                        var store = this.getPanelPartInscricao().getStore();

                                        store.baseParams = {
                                            capacitacao: store.baseParams.capacitacao,
                                            start: 0,
                                            limit: 50,
                                            query: new_value
                                        };

                                        store.load({});
                                    }
                                }
                            }
                        ]
                    });
                }

                return this.inscricaoToolbar;
            }

        }
    );
}
