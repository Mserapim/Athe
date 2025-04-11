
Ext.ns('toolkit.engine.job');

toolkit.engine.job.JobManage = Ext.extend(
    Ext.Panel,
    {
        constructor: function() {
            var cf = {
                title: 'Gerenciador de Tarefas',
                closable: true,
                bbar: new Ext.Toolbar({
                    frame: true,
                    layout: 'column',
                    items: [
                        {
                            xtype: 'panel',
                            frame: true,
                            html: '<span>Test</span>',
                            width: 683
                        },
                        ' ',
                        {
                            xtype: 'panel',
                            width: 125,
                            frame: true,
                            html: '<span>Test</span>'
                        },
                        ' ',
                        {
                            xtype: 'panel',
                            width: 125,
                            frame: true,
                            html: '<span>Test</span>'
                        },
                        ' ',
                    ]
                }),
                tbar: [
                    {
                        text: 'Nova',
                        iconCls: true,
                        menu: [
                            {
                                text: 'Diaria'
                            },
                            {
                                text: 'Semanal'
                            },
                            {
                                text: 'Mensal'
                            }
                        ]
                    },
                    {
                        text: 'Editar',
                        iconCls: true
                    },
                    {
                        text: 'Remover',
                        iconCls: true
                    },
                    '-',
                    {
                        text: 'Executar',
                        iconCls: true
                    },
                    '-',
                    ' ',
                    {
                        xtype: 'label',
                        text: 'Buscar por : '
                    },
                    ' ',
                    ' ',
                    {
                        xtype: 'textfield',
                        emptyText: 'Informa o texto a ser buscado.',
                        width: 300
                    },
                    ' ',
                    ' ',
                    {
                        text: 'Buscar',
                        iconCls: true
                    },
                    '-',
                    '->',
                    '-'
                ]
            }

            toolkit.engine.job.JobManage.superclass.constructor.call(this, cf);

            var ts = toolkit.Application.tabspace;
            var ap = ts.getActiveTab();

            ts.remove(ap);
            ts.add(this);
            ts.setActiveTab(this);
        }
    }
);