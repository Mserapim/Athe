Ext.ns('toolkit.common.poll');
toolkit.common.icons = '/'+CONTEXT+'/static/common/icons/';
toolkit.common.poll.delete = function(opts)
{
    Ext.Msg.confirm(
        'Confirmação',
        opts.message,
        function(btn)
        {
            if(btn == 'yes')
            {
                Ext.Ajax.request({
                    url: action('SafePolls/delete/json'),
                    params: { model:opts.model, id: opts.id, poll: opts.poll || '' },
                    success: function(response)
                    {
                        var json = Ext.decode(response.responseText);
                        if( json.success )
                            opts.store.reload();
                        else
                            Ext.Msg.alert('Erro', json.msg);
                    }
                });
            }
        }
    );
}

toolkit.common.poll.Polls = Ext.extend(Ext.Panel, {
    constructor: function()
    {
        toolkit.common.poll.Polls.superclass.constructor.call(this, {
            id: 'common-polls',
            closable: true,
            title: 'Votações',
            layout: 'fit',
            items: [this._getPollsGrid()],
            tbar: [
                {
                    tooltip:'Criar nova votação.',
                    icon: toolkit.common.icons+'add.png',
                    text: 'Nova',
                    handler: function()
                    { this._makeForm({title:'Criar Votação', vals:{}, readonly: false}).show(); },
                    scope:this
                }
            ],
            bbar: [this._getPollsPagination()],
            listeners: {
                render: function(cmp)
                { new Ext.LoadMask(cmp.getEl(), {msg:'Por favor aguarde...', store:this._getPollsStore()}); }
            }
        });

        if(Ext.getCmp('common-polls'))
        {
            toolkit.Application.tabspace.add(this);
            this.show();
        }
    },

    _getPollsStore: function()
    {
        if(!this._pollsStore)
        {
            this._pollsStore = new Ext.data.JsonStore({
                scope: this,
                autoLoad: true,
                root: 'result',
                totalProperty: 'total',
                fields: [
                    'id', 'title', 'key', 'finished', 'published',
                    'locked', 'counted', 'updating_allowed_list', 'slug',
                    'max_of_choices', 'publication_start', 'publication_end', 'target'
                ],
                baseParams: { start:0, end:50 },
                proxy: new Ext.data.HttpProxy({
                    method:'GET',
                    url: action('SafePolls/all/json')
                }),
                listeners: {
                    load: function()
                    {
                        Ext.select('.athenas-published').set({src:toolkit.common.icons+'published.png'});
                        Ext.select('.athenas-non-published').set({src:toolkit.common.icons+'no-published.png'});
                        Ext.select('.athenas-edit').set({src:toolkit.common.icons+'edit.png'});
                        Ext.select('.athenas-delete').set({src:toolkit.common.icons+'delete.png'});
                        Ext.select('.athenas-report').set({src:toolkit.common.icons+'report.png'});
                        Ext.select('.athenas-simple-report').set({src:toolkit.common.icons+'report2.png'});
                        Ext.select('.able-voters').set({src:toolkit.common.icons+'able-voters.png'});
                        //Ext.select('.athenas-voters').set({src:toolkit.common.icons+'report2.png'});
                        Ext.select('.athenas-count').set({src:toolkit.common.icons+'count.png'});
                        Ext.select('.athenas-denied').set({src:toolkit.common.icons+'denied.png'});
                    }
                }
            });
        }
        return this._pollsStore;
    },

    _getPollsConditionsStore: function()
    {
        if(!this._pollsConditionsStore)
        {
            this._pollsConditionsStore = new Ext.data.JsonStore({
                autoLoad:true,
                fields: ['id', 'description'],
                proxy: new xt.data.HttpProxy({
                    method:'GET',
                    url: action('SafePolls/conditions/json')
                }),
                baseParams:{ start:0, end:50 }
            });
        }
        return this._pollsConditionsStore;
    },

    _getPollsGrid: function()
    {
        if(!this._pollsGrid)
        {
            var booleanRenderer = function (val){ return (val) ? 'Sim' : 'Não'; };
            var emptyRenderer = function (val){ return val || '----------' }
            this._pollsGrid = new Ext.grid.GridPanel({
                scope:this,
                region:'center',
                border:true,
                store: this._getPollsStore(),
                columns:
                [
                    {dataIndex:'title', header:'Votação', width:368 },
                    {dataIndex:'published', header:'Publicada?', width:70, renderer: booleanRenderer },
                    {dataIndex:'publication_start', header:'Data de inicio', width:100, renderer: emptyRenderer },
                    {dataIndex:'publication_end', header:'Data de término', width:100, renderer: emptyRenderer },
                    {dataIndex:'finished', header:'Finalizada?', width:70, renderer: booleanRenderer },
                    {dataIndex:'target', header:'Público alvo', width:150, renderer: function(list) {
                        var lis = [];
                        Ext.each(list, function(item){
                            lis[lis.length] = { tag:'li', html: item.description };
                        });

                        return Ext.DomHelper.markup({
                            tag:'ul',
                            children:lis
                        });
                    }},
                    {dataIndex:'updating_allowed_list', header:'Lista de aptos', width:150, renderer: function(val) {
                        return (val) ? 'Processando...' : 'Atualizada';
                    }},
                    {
                        xtype: 'actioncolumn',
                        header:'Controles',
                        width: 110,
                        scope: this,
                        items:
                        [
                            {
                                tooltip:'Opções de voto',
                                icon: toolkit.common.icons+'choice.png',
                                handler:function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row)
                                    new toolkit.common.poll.Choices(record.get('id'), record.get('title')).show();
                                },
                                scope:this
                            },
                            {
                                tooltip:'Usuários bloqueados',
                                icon: toolkit.common.icons+'denied.png',
                                handler:function(grid, row, col)
                                {
                                    var _this = this,
                                        record = grid.getStore().getAt(row),
                                        blackList = new toolkit.common.poll.BlackList(record.get('id'));

                                    blackList.on('close', function(){
                                        if(!record.get('locked'))
                                            _this._updateAllowedList(record.get('id'))
                                    });

                                    blackList.show();
                                },
                                scope:this
                            },
                            {
                                tooltip:'Usuários aptos',
                                getClass:function(val, meta, record)
                                { return !record.get('updating_allowed_list') ? 'able-voters' : ''; },
                                handler:function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row);
                                    if(!record.get('updating_allowed_list'))
                                    {
                                        engine.mq.Report.request({
                                            report: '/to/mpe/votacao/Extrato_Aptos',
                                            params: {
                                                poll: record.get('id'),
                                                outfile: 'lista-de-aptos-eleicao-' + record.get('slug'),
                                                report_name: 'Lista de aptos da eleição ' + record.get('title')
                                            },
                                            el: this.getEl(),
                                            waitMessage: 'Gerando relatório...',
                                        });


                                        // new toolkit.widget.ExtReportBuild('SafePollAbleVoters', '/to/mpe/votacao/extratoaptos/resultado_votacao').runReport(
                                        //     '', { poll: record.get('id') }
                                        // );
                                    }
                                },
                                scope:this
                            },
                            {
                                tooltip:'Publicação de votação',
                                getClass:function(val, meta, record)
                                { return !record.get('locked') ? 'athenas-non-published' : ''; },
                                handler:function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row)
                                    this._makePublicationForm({
                                        title:'Agendamento de publicação',
                                        vals:{
                                            poll: record.get('id'),
                                            start: record.get('publication_start'),
                                            end: record.get('publication_end')
                                        }
                                    }).show();
                                },
                                scope:this
                            },
                            {
                                tooltip:'Iniciar apuração',
                                getClass:function(val, meta, record)
                                { return record.get('finished') && !record.get('counted') ? 'athenas-count' : ''; },
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row);
                                    this._makeCountForm({
                                        title: 'Apurar votos de '+ record.get('title'),
                                        vals: { poll: record.get('id') },
                                        success: function(result)
                                        { Ext.Msg.alert('Alerta', result.msg) }
                                    }).show();
                                }
                            },
                            /*{
                                tooltip:'Parcial de não votantes',
                                icon: toolkit.common.icons+'warnning.png',
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row);
                                    new toolkit.widget.ExtReportBuild('SafePollNonVotersReport', '/to/mpe/votacao/extratonaovotante/resultado_votacao').runReport(
                                        '', { poll: record.get('id') }
                                    );
                                }
                            },*/
                            {
                                tooltip:'Resultado detalhado',
                                getClass:function(val, meta, record)
                                { return record.get('finished') && record.get('counted') ? 'athenas-report' : ''; },
                                handler: function(grid, row, col)
                                {
                                    var _this = this,
                                        record = grid.getStore().getAt(row);

                                    this._makeCountForm({
                                        title: 'Gerar resultado detalhado de "' + record.get('title') + '"',
                                        vals: { poll: record.get('id') },
                                        success: function(result)
                                        {
                                            Ext.Msg.alert('Alerta', result.msg + 'Aguarde notificação de conclusão do relatório')

                                            engine.mq.Report.request({
                                                report: '/to/mpe/votacao/Extrato_Eleicao',
                                                params: {
                                                    poll: record.get('id'),
                                                    outfile: 'resultado-detalhado-eleicao-' + record.get('slug'),
                                                    report_name: 'Resultado detalhado da eleição ' + record.get('title')
                                                },
                                                el: _this.getEl(),
                                                waitMessage: 'Gerando relatório...',
                                            });
                                        }
                                    }).show();


                                    // new toolkit.widget.ExtReportBuild('SafePollReport', '/to/mpe/votacao/extratoeleicao/resultado_votacao').runReport(
                                    //     '', { poll: record.get('id') }
                                    // );
                                }
                            },
                            {
                                tooltip:'Lista tríplice',
                                getClass:function(val, meta, record)
                                { return record.get('finished') && record.get('counted') ? 'athenas-simple-report' : ''; },
                                handler: function(grid, row, col)
                                {
                                    var _this = this,
                                        record = grid.getStore().getAt(row);
                                    this._makeCountForm({
                                        title: 'Gerar lista tríplice de "' + record.get('title') + '"',
                                        vals: { poll: record.get('id') },
                                        success: function(result)
                                        {
                                            Ext.Msg.alert('Alerta', result.msg + 'Aguarde notificação de conclusão do relatório')

                                            engine.mq.Report.request({
                                                report: '/to/mpe/votacao/Extrato_Eleicao_Final',
                                                params: {
                                                    poll: record.get('id'),
                                                    outfile: 'resultado-sintetico-eleicao-' + record.get('slug'),
                                                    report_name: 'Resultado sintético da eleição ' + record.get('title')
                                                },
                                                el: _this.getEl(),
                                                waitMessage: 'Gerando relatório...',
                                            });
                                        }
                                    }).show();

                                    // new toolkit.widget.ExtReportBuild('SafePollSimpleReport', '/to/mpe/votacao/extratoeleicaofinal/resultado_votacao').runReport(
                                    //     '', { poll: record.get('id') }
                                    // );
                                }
                            },
                            {
                                tooltip:'Visualizar votação',
                                getClass:function(val, meta, record)
                                { return !record.get('locked') ? 'athenas-edit' : ''; },
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row)
                                    this._makeForm({
                                        title: 'Visualizar votação (Campos somente leitura)',
                                        vals: {
                                            id: record.get('id'),
                                            title: record.get('title'),
                                            max_of_choices: record.get('max_of_choices'),
                                            target: record.get('target')[0],
                                            key: record.get('key'),
                                            confirm_key: record.get('key')
                                        },
                                        readonly: true
                                    }).show();
                                },
                                scope:this
                            },
                            {
                                tooltip: 'Excluir votação',
                                getClass:function(val, meta, record)
                                { return !record.get('locked') ? 'athenas-delete' : ''; },
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row);
                                    toolkit.common.poll.delete({
                                        model: 'Poll',
                                        id: record.get('id'),
                                        store: grid.getStore(),
                                        message: 'Confirma exclusão da votação "'+ record.get('title') +'" ?'
                                    });
                                },
                                scope:this
                            }
                        ]
                    }
                ]
            });
        }
        return this._pollsGrid;
    },

    _getPollsPagination: function()
    {
        if(!this._pollsPagination)
        {
            this._pollsPagination = new Ext.PagingToolbar({
                store: this._getPollsStore(),
                displayInfo: true,
                pageSize: 15,
                prependButtons: true
            });

        }
        return this._pollsPagination;
    },

    _showResult: function(data)
    {
        var template = new Ext.XTemplate([
            '<tpl for=".">',
                '<div style="padding:10px;">',
                    '<p style="font-size:13px; margin: 5px 0;"><b style="margin-right:5px;">{label}:</b>{value}</p>',
                '</div>',
            '</tpl>'
        ]);

        new Ext.Window({
            title: 'Resultado',
            html: template.apply(data)
        }).show();
    },

    _makeCountForm: function(opts)
    {
        // var showResult = this._showResult;

        return ExtFormHelper({
            url: action('SafePolls/count/json'),
            timeout: 120,
            store: this._getPollsStore(),
            success: function (form, action)
            {
                if (opts.success)
                    opts.success(action.result);
            },
            windowConfig: {
                title: opts.title
            },
            formConfig: {
                autoWidth: true,
                autoHeight: true,
                items: [
                    {
                        id: 'poll',
                        name: 'poll',
                        value: opts.vals.poll || '',
                        xtype: 'hidden'
                    },
                    {
                        id: 'key',
                        name: 'key',
                        fieldLabel: 'Chave de segurança',
                        xtype: 'textfield',
                        inputType: 'password',
                        width: 250
                    }
                ]
            }
        });
    },

    _makePublicationForm: function(opts)
    {
        return ExtFormHelper({
            url: action('SafePolls/publication/json'),
            store: this._getPollsStore(),
            windowConfig: {
                title: opts.title
            },
            formConfig: {
                autoWidth: true,
                autoHeight: true,
                items: [
                    {
                        id: 'poll',
                        name: 'poll',
                        value: opts.vals.poll || '',
                        xtype: 'hidden'
                    },
                    {
                        id: 'start',
                        fieldLabel: 'Data de inicio',
                        name: 'start',
                        value: opts.vals.start || '',
                        format: 'd/m/Y H:M',
                        xtype: 'tk-datetimefield'
                    },
                    {
                        id: 'end',
                        fieldLabel: 'Data fim',
                        name: 'end',
                        value: opts.vals.end || '',
                        format: 'd/m/Y H:M',
                        xtype: 'tk-datetimefield'
                    }
                ]
            }
        });
    },

    _updateAllowedList: function(poll_id)
    {
        var _this = this;
        Ext.Ajax.request({
            url: toolkit.util.action('SafePolls/update_allowed_list/' + poll_id + '/json'),
            success: function(response)
            {
                var obj = Ext.decode(response.responseText);
                if(obj.success)
                {
                    _this._getPollsStore().reload();
                    _this._checkAllowedListUpdating(obj.task_uuid)
                }
            }
        });
    },

    _checkAllowedListUpdating: function(uuid)
    {
        var _this = this,
            interval = setInterval(function() {
                Ext.Ajax.request({
                    url: toolkit.util.action('SafePolls/check_task/' + uuid + '/json'),
                    success: function(response)
                    {
                        var obj = Ext.decode(response.responseText);
                        if(obj.success)
                        {
                            clearInterval(interval);
                            _this._getPollsStore().reload();
                        }
                    }
                });
            }, 5000);
    },

    _makeForm: function(opts)
    {
        var _this = this;

        return ExtFormHelper({
            url: action('SafePolls/add_or_edit/json'),
            store: this._getPollsStore(),
            success: function(form, action)
            {
                if(action.result.success && action.result.task_uuid)
                {
                    var uuid = action.result.task_uuid;
                    _this._checkAllowedListUpdating(uuid);
                }
            },
            windowConfig: {
                title: opts.title
            },
            formConfig: {
                autoWidth: true,
                autoHeight: true,
                items: [
                    {
                        id: 'id',
                        name: 'id',
                        value: opts.vals.id || '',
                        xtype: 'hidden'
                    },
                    {
                        id: 'title',
                        fieldLabel: 'Votação',
                        name: 'title',
                        value: opts.vals.title || '',
                        width: 350,
                        xtype: 'textfield',
                        readOnly: opts.readonly
                    },
                    {
                        id: 'max_of_choices',
                        fieldLabel: 'Máximo votos por pessoa',
                        name: 'max_of_choices',
                        value: opts.vals.max_of_choices || '',
                        width: 50,
                        xtype: 'textfield',
                        readOnly: opts.readonly
                    },
                    {
                        id: 'target',
                        fieldLabel: 'Público alvo',
                        hiddenName: 'target',
                        hiddenValue: (opts.vals.target) ? opts.vals.target.id : '',
                        mode: 'local',
                        value: (opts.vals.target) ? opts.vals.target.description : '',
                        xtype: 'combo',
                        triggerAction: 'all',
                        width: 350,
                        valueField: 'id',
                        displayField: 'description',
                        store: this._getPollsConditionsStore(),
                        readOnly: opts.readonly
                    },
                    {
                        id: 'key',
                        name: 'key',
                        fieldLabel: 'Chave de segurança',
                        xtype: 'textfield',
                        inputType: 'password',
                        value: opts.vals.key || '',
                        width: 250,
                        readOnly: opts.readonly
                    },
                    {
                        id: 'confirm_key',
                        name: 'confirm_key',
                        fieldLabel: 'Confirmação de chave de segurança',
                        xtype: 'textfield',
                        inputType: 'password',
                        value: opts.vals.key || '',
                        width: 250,
                        readOnly: opts.readonly
                    }
                ]
            }
        });
    }
});

toolkit.common.poll.Choices = Ext.extend(Ext.Window, {
    constructor: function(poll, title)
    {
        this.poll = poll;
        toolkit.common.poll.Choices.superclass.constructor.call(this, {
            title: 'Opções da votação '+title,
            layout: 'fit',
            modal: true,
            height: 280,
            width: 380,
            items: [this._getChoicesGrid()],
            tbar: [
                {
                    tooltip:'Criar opção.',
                    icon: toolkit.common.icons+'add.png',
                    text: 'Nova',
                    handler: function()
                    { this._makeForm({title:'Criar opção', vals:{poll:this.poll}}).show(); },
                    scope:this
                }
            ]
        });

    },

    _getChoicesStore: function()
    {
        if(!this._choicesStore)
        {
            this._choicesStore = new Ext.data.JsonStore({
                autoLoad:true,
                root: 'result',
                totalProperty: 'total',
                fields: ['id', 'choice', 'locked'],
                proxy: new Ext.data.HttpProxy({
                    method:'GET',
                    url: action('SafePolls/choices/json')
                }),
                baseParams:{ start:0, end:50, poll:this.poll },
                listeners:{
                    load:function()
                    {
                        Ext.select('.athenas-edit').set({src:toolkit.common.icons+'edit.png'});
                        Ext.select('.athenas-delete').set({src:toolkit.common.icons+'delete.png'});
                    }
                }
            });
        }
        return this._choicesStore;
    },

    _getChoicesGrid: function()
    {
        if(!this._choicesGrid)
        {
            this._choicesGrid = new Ext.grid.GridPanel({
                scope:this,
                region:'center',
                border:true,
                store: this._getChoicesStore(),
                columns:
                [
                    {dataIndex:'choice', header:'Opção', width:300},
                    {
                        xtype: 'actioncolumn',
                        header:'Controles',
                        width: 60,
                        scope:this,
                        items:
                        [
                            {
                                tooltip:'Editar opção',
                                getClass:function(val, meta, record)
                                { return !record.get('locked') ? 'athenas-edit' : ''; },
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row)
                                    this._makeForm({
                                        title:'Editar opção',
                                        vals:{
                                            poll: this.poll,
                                            id:record.get('id'),
                                            choice:record.get('choice')
                                        }
                                    }).show();
                                },
                                scope:this
                            },
                            {
                                tooltip: 'Excluir alternativa',
                                getClass:function(val, meta, record)
                                { return !record.get('locked') ? 'athenas-delete' : ''; },
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row);
                                    toolkit.common.poll.delete({
                                        model: 'Choice',
                                        id: record.get('id'),
                                        store: grid.getStore(),
                                        message: 'Confirma exclusão da opção "'+ record.get('choice') +'" ?'
                                    });
                                },
                                scope:this
                            }
                        ]
                    }
                ]
            });
        }
        return this._choicesGrid;
    },

    _makeForm: function(opts)
    {
        return ExtFormHelper({
            url:action('SafePolls/add_or_edit_choice/json'),
            store:this._getChoicesStore(),
            windowConfig:{
                title:opts.title,
                frame:true,
            },
            formConfig:{
                autoWidth:true,
                autoHeight:true,
                items:[
                    {
                        id:'poll',
                        name:'poll',
                        value: opts.vals.poll || '',
                        xtype:'hidden'
                    },
                    {
                        id:'id',
                        name:'id',
                        value: opts.vals.id || '',
                        xtype:'hidden'
                    },
                    {
                        id:'choice',
                        fieldLabel:'Alternativa',
                        name:'choice',
                        value: opts.vals.choice || '',
                        width:350,
                        xtype:'textfield'
                    }
                ]
            }
        });
    }
});


toolkit.common.poll.VotePolls = Ext.extend(Ext.Window, {
    constructor: function(store)
    {
        this.finished = 0;
        toolkit.common.poll.VotePolls.superclass.constructor.call(this, {
            id: 'polls-list',
            title: 'Em andamento',
            layout: 'fit',
            modal: true,
            height: 300,
            width: 400,
            tbar: [
                {
                    text:'Em andamento',
                    handler: function()
                    {
                        this.setTitle('Em andamento');
                        this.finished = 0;
                        this._getPollsStore().load({params:{finished:this.finished}});
                    },
                    scope: this
                },
                '-',
                {
                    text:'Finalizadas',
                    handler: function()
                    {
                        this.setTitle('Finalizadas');
                        this.finished = 1;
                        this._getPollsStore().load({params:{finished:this.finished}});
                    },
                    scope: this
                }
            ],
            items: [ this._getPollsGrid() ],
            bbar: [ this._getPollsPagination() ]
        });
    },

    _getPollsStore: function()
    {
        if(!this._pollsStore)
        {
            this._pollsStore = new Ext.data.JsonStore({
                autoLoad:true,
                root: 'result',
                totalProperty: 'total',
                fields: ['id', 'title', 'voted', 'max_of_choices', 'choices', 'finished'],
                proxy: new Ext.data.HttpProxy({
                    method:'GET',
                    url: action('SafePolls/get/json')
                }),
                baseParams:{ start:0, end:15, finished: this.finished },
                listeners:{
                    load: function(store)
                    {
                        Ext.select('.athenas-choice').set({src:toolkit.common.icons+'choice.png'});
                        Ext.select('.athenas-poll').set({src:toolkit.common.icons+'poll.png'});

                        var record = store.getAt(0);
                        if( store.getCount() == 1 && !record.get('voted') && !record.get('finished'))
                        {
                            this._makeForm({
                                store: store,
                                vals:{
                                    poll: record.get('id'),
                                    title: record.get('title'),
                                    choices: record.get('choices'),
                                    max_chosen: record.get('max_of_choices')
                                }
                            }).show();
                            this.close();
                        }
                    },
                    scope: this
                }
            });
        }
        return this._pollsStore;
    },

    _getPollsGrid: function()
    {
        if(!this._pollsGrid)
        {
            this._pollsGrid = new Ext.grid.GridPanel({
                scope:this,
                region:'center',
                border:true,
                store: this._getPollsStore(),
                columns:
                [
                    {dataIndex:'title', header:'Votação', width:300},
                    {
                        xtype: 'actioncolumn',
                        header:'Controles',
                        width: 60,
                        scope:this,
                        items:
                        [
                            {
                                tooltip:'Votar',
                                getClass:function(val, meta, record)
                                { return !record.get('voted') && !record.get('finished') ? 'athenas-choice' : ''; },
                                handler:function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row)
                                    this._makeForm({
                                        store: grid.getStore(),
                                        vals:{
                                            poll: record.get('id'),
                                            title: record.get('title'),
                                            choices: record.get('choices'),
                                            max_chosen: record.get('max_of_choices')
                                        }
                                    }).show();
                                },
                                scope:this
                            }
                        ]
                    }
                ]
            });
        }
        return this._pollsGrid;
    },

    _getPollsPagination: function()
    {
        if(!this._pollsPagination)
        {
            this._pollsPagination = new Ext.PagingToolbar({
                store: this._getPollsStore(),
                displayInfo: true,
                pageSize: 15,
                prependButtons: true
            });
        }
        return this._pollsPagination;
    },

    getFormPanel: function(opts) {
        if(!this._formPanel) {
            var token_message = opts.vals.max_chosen + ((opts.vals.max_chosen > 1) ? ' opções' : ' opção');
            var message = '<span style="font-style:italic;">* Se nenhuma opção for selecionada seu voto será computado como BRANCO.</span></br></br>'+
            '<span style="font-style:italic;">* Se for selecionado a opção do voto nulo ou mais que '+ token_message +' de candidato(s), o seu voto será computado como NULO.<span></br></br>';

            var choices = [];
            Ext.each(opts.vals.choices, function(item) {
                choices[choices.length] = {boxLabel: item.choice, name: 'choice', inputValue: item.id};
            });

            this._formPanel = new Ext.form.FormPanel({
                labelWidth:125,
                labelAlign:'top',
                bodyStyle:'padding:5px;',
                border:false,
                autoScroll: true,
                maxHeight: 500,
                width: 410,
                items: [
                    {
                        id:'poll',
                        name:'poll',
                        value: opts.vals.poll || '',
                        xtype:'hidden'
                    },
                    {
                        html: '<span style="font-style:italic; font-weight:bold;">'+opts.vals.title+'</span>',
                        width:400,
                        xtype:'displayfield'
                    },
                    {
                        id:'choices',
                        fieldLabel: 'Alternativas',
                        hideLabel: true,
                        columns: 1,
                        xtype:'checkboxgroup',
                        width:400,
                        items: choices
                    },
                    {
                        html: message,
                        width:400,
                        xtype:'displayfield'
                    }
                ],
                buttons: [
                    {
                        text: '<span style="color:red; font-weight:bold;">Nulo</span>',
                        handler: function(btn)
                        {
                            var voted = [{boxLabel: 'NULO', name: 'choice', inputValue: 'NULO'}];
                            this._makeConfirmForm(opts.vals.poll, voted, opts.vals.max_chosen).show();
                        },
                        scope: this
                    },
                    {
                        text: '<span style="color:green; font-weight:bold;">Votar</span>',
                        handler: function(btn)
                        {
                            var voted = this.getFormPanel().findById('choices').getValue();
                            this._makeConfirmForm(opts.vals.poll, voted, opts.vals.max_chosen).show();
                        },
                        scope: this
                    }
                ]
            });
        }

        return this._formPanel;
    },

    _makeForm: function(opts)
    {
        if(!this.windowForm) {
            this.windowForm = new Ext.Window({
                id: 'vote-form',
                title:'Urna Eletrônica',
                frame: true,
                modal: true,
                closable: true,
                items: this.getFormPanel(opts)
            });
        }

        return this.windowForm;
    },

    _makeConfirmForm: function(poll, choices, max_chosen)
    {
        var items = [];
        var chosen = [];

        Ext.each(choices, function(item) {
            items[items.length] = { tag: 'li', html: item.boxLabel, style:'list-style: square inside; font-weight:bold;' };
            chosen[chosen.length] = item.inputValue;
        });

        if (choices.length < max_chosen && chosen.indexOf('NULO') == -1)
        {
            var i;
            var whites = max_chosen - choices.length;
            for(i=0; i<whites; i++)
                items[items.length] = { tag: 'li', html: 'BRANCO', style:'list-style: square inside; font-weight:bold;' };
        }
        else if (choices.length > max_chosen)
            items = [{ tag: 'li', html: 'NULO', style: 'list-style: square inside; font-weight:bold;'}];

        var votes = {
            tag: 'div',
            children: [
                { tag: 'p', html: 'Você selecionou:' },
                { tag: 'ul', children: items }
            ]
        };
        var message = '<span style="font-style:italic;">Para confirmar seu voto digite sua senha e clique no botão confirmar, caso queira corrigir seu voto clique em corrigir.</span></br></br>';

        var confirm = new Ext.form.FormPanel({
            labelWidth: 125,
            labelAlign: 'top',
            bodyStyle: 'padding:5px;',
            border: false,
            autoScroll: true,
            maxHeight: 500,
            width: 260,
            items: [
                {
                    html: Ext.DomHelper.markup(votes),
                    width:250,
                    xtype:'displayfield'
                },
                {
                    html: message,
                    width: 250,
                    xtype:'displayfield'
                },
                {
                    id: 'password',
                    name: 'password',
                    fieldLabel: 'Senha',
                    xtype: 'textfield',
                    inputType: 'password',
                    width: 250
                }
            ],
            buttons: [
                {
                    text: '<span style="color:red; font-weight:bold;">Corrigir</span>',
                    handler: function()
                    { Ext.getCmp('confirm-form').destroy(); }
                },
                {
                    text: '<span style="color:green; font-weight:bold;">Confirmar</span>',
                    handler: function(btn)
                    {
                        var loading = new Ext.LoadMask(confirm.el, {msg:'Por favor aguarde...'});
                        loading.show();
                        Ext.Ajax.request({
                            url: action('SafePolls/vote/json'),
                            params: {votes: chosen.toString(), poll: poll, password: confirm.findById('password').getValue() },
                            success: function(response)
                            {
                                loading.hide();
                                var json = Ext.decode(response.responseText);
                                if(json.success)
                                {
                                    Ext.getCmp('vote-form').destroy();
                                    Ext.getCmp('confirm-form').destroy();
                                    if( Ext.getCmp('polls-list') )
                                        Ext.getCmp('polls-list').destroy();
                                    Ext.Msg.alert('Confirmação', 'Seu voto foi computado com sucesso.');
                                }
                                else
                                    showErrorMessage(json, confirm);
                            }
                        });

                    }
                }
            ]
        });

        return new Ext.Window({
            id: 'confirm-form',
            title:'Confirmação de voto',
            frame: true,
            modal: true,
            items: [confirm]
        });
    }
});


toolkit.common.poll.BlackList = Ext.extend(Ext.Window, {
    constructor: function(poll)
    {
        this._poll = poll;
        toolkit.common.poll.BlackList.superclass.constructor.call(this, {
            title:'Usuários bloqueados',
            modal:true,
            width:420,
            height:350,
            layout:'fit',
            defaults:{margins:'2 2 2 2'},
            items: [this._getBlockedUsers()],
            listeners: {
                render: function(cmp)
                { new Ext.LoadMask(cmp.getEl(), {msg:'Por favor aguarde...', store:this._getStore()}); }
            }
        });
    },

    _getStore: function()
    {
        if(!this._store)
        {
            this._store = new Ext.data.JsonStore({
                autoLoad:true,
                root: 'result',
                totalProperty: 'total',
                fields: ['id', 'username', 'fullname', 'email'],
                proxy: new xt.data.HttpProxy({
                    method:'GET',
                    url: action('SafePolls/blocked_users/json')
                }),
                baseParams:{ start:0, limit:20, poll:this._poll },
                scope:this,
                listeners:{
                    load:function()
                    { Ext.select('.athenas-delete').set({src:toolkit.common.icons+'delete.png'}); },
                    scope:this
                }
            });
        }
        return this._store;
    },

    _getBlockedUsers: function()
    {
        if(!this._blockedUsers)
        {
            this._blockedUsers = new Ext.grid.GridPanel({
                scope:this,
                store:this._getStore(),
                tbar: [
                    {
                        tooltip:'Adicionar usuários',
                        icon: toolkit.common.icons+'add.png',
                        text: 'Adicionar',
                        handler: function()
                        { this._makeForm({title:'Adicionar Usuário', vals:{poll:this._poll}}).show(); },
                        scope:this
                    }
                ],
                columns:
                [
                    {dataIndex:'fullname', header:'Usuário', width:200},
                    {dataIndex:'email', header:'Email', width:170},
                    {
                        xtype: 'actioncolumn',
                        width: 30,
                        scope:this,
                        items: [
                            {
                                tooltip: 'Excluir',
                                icon: toolkit.common.icons+'delete.png',
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row);
                                    toolkit.common.poll.delete({
                                        model: 'User',
                                        id: record.get('id'),
                                        poll: this._poll,
                                        store: grid.getStore(),
                                        message: 'Confirma exclusão do servidor "'+ record.get('fullname') +'" da lista de bloqueados?'
                                    });
                                },
                                scope:this
                            }
                        ]
                    }
                ],
                bbar: new Ext.PagingToolbar({
                    store: this._getStore(),
                    displayInfo: true,
                    pageSize: 20,
                    prependButtons: true
                })
            });
        }
        return this._blockedUsers;
    },

    _makeForm: function(opts)
    {
        return ExtFormHelper({
            url: action('SafePolls/block_user/json'),
            store: this._getStore(),
            width:300,
            height:150,
            windowConfig: {
                title: opts.title,
                frame:true,
            },
            formConfig:{
                autoWidth:true,
                autoHeight:true,
                items:[
                    {
                        id:'poll',
                        name:'poll',
                        value: opts.vals.poll || '',
                        xtype:'hidden'
                    },
                    {
                        id: 'user',
                        xtype: 'combo',
                        width: 270,
                        scope: this,
                        triggerAction: 'all',
                        lazyRender: true,
                        valueField: 'id',
                        displayField: 'fullname',
                        fieldLabel: 'Digite o nome do servidor',
                        hiddenName: 'user',
                        store: new Ext.data.JsonStore({
                            root: 'result',
                            totalProperty: 'total',
                            remoteSort: true,
                            fields: ['id', 'fullname'],
                            url: action('SafePolls/users/json')
                        })
                    }
                ]
            }
        });
    }
});


