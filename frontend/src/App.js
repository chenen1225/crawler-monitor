import React, { useState, useEffect } from 'react';
import { Layout, Menu, Button, Row, Col, Card, Table, Form, Input, Select, DatePicker, message } from 'antd';
import axios from 'axios';

const { Header, Content, Sider } = Layout;
const { Option } = Select;

const App = () => {
  const [currentView, setCurrentView] = useState('dashboard');
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [sites, setSites] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [results, setResults] = useState([]);

  const API_BASE = 'http://localhost:8000/api/v1';

  // 获取网站列表
  const fetchSites = async () => {
    try {
      const response = await axios.get(`${API_BASE}/sites/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSites(response.data);
    } catch (error) {
      message.error('获取网站列表失败');
    }
  };

  // 获取关键词列表
  const fetchKeywords = async () => {
    try {
      const response = await axios.get(`${API_BASE}/keywords/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setKeywords(response.data);
    } catch (error) {
      message.error('获取关键词列表失败');
    }
  };

  // 获取任务列表
  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API_BASE}/tasks/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTasks(response.data);
    } catch (error) {
      message.error('获取任务列表失败');
    }
  };

  // 获取爬取结果
  const fetchResults = async () => {
    try {
      const response = await axios.get(`${API_BASE}/results/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setResults(response.data);
    } catch (error) {
      message.error('获取爬取结果失败');
    }
  };

  useEffect(() => {
    if (token) {
      fetchSites();
      fetchKeywords();
      fetchTasks();
      fetchResults();
    }
  }, [token]);

  const handleLogin = async (values) => {
    try {
      const response = await axios.post(`${API_BASE}/auth/login`, {
        username: values.email,
        password: values.password
      });
      
      const { access_token } = response.data;
      setToken(access_token);
      localStorage.setItem('token', access_token);
      message.success('登录成功');
    } catch (error) {
      message.error('登录失败');
    }
  };

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('token');
    message.info('已退出登录');
  };

  const handleRegister = async (values) => {
    try {
      await axios.post(`${API_BASE}/auth/register`, {
        email: values.email,
        password: values.password
      });
      message.success('注册成功，请登录');
    } catch (error) {
      message.error('注册失败');
    }
  };

  // 添加新网站
  const addSite = async (values) => {
    try {
      await axios.post(`${API_BASE}/sites/`, values, {
        headers: { Authorization: `Bearer ${token}` }
      });
      message.success('网站添加成功');
      fetchSites();
    } catch (error) {
      message.error('添加网站失败');
    }
  };

  // 添加新关键词
  const addKeyword = async (values) => {
    try {
      await axios.post(`${API_BASE}/keywords/`, values, {
        headers: { Authorization: `Bearer ${token}` }
      });
      message.success('关键词添加成功');
      fetchKeywords();
    } catch (error) {
      message.error('添加关键词失败');
    }
  };

  // 添加新任务
  const addTask = async (values) => {
    try {
      await axios.post(`${API_BASE}/tasks/`, {
        name: values.name,
        description: values.description,
        frequency: values.frequency,
        site_ids: values.site_ids,
        keyword_ids: values.keyword_ids
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      message.success('任务添加成功');
      fetchTasks();
    } catch (error) {
      message.error('添加任务失败');
    }
  };

  const menuItems = [
    { key: 'dashboard', label: '仪表板' },
    { key: 'sites', label: '监控网站' },
    { key: 'keywords', label: '监控关键词' },
    { key: 'tasks', label: '爬虫任务' },
    { key: 'results', label: '爬取结果' }
  ];

  if (!token) {
    return (
      <Layout style={{ minHeight: '100vh' }}>
        <Content style={{ padding: '50px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Card title="爬虫监控系统登录" style={{ width: 400 }}>
            <LoginForm onLogin={handleLogin} onRegister={handleRegister} />
          </Card>
        </Content>
      </Layout>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header className="header" style={{ color: '#fff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ color: '#fff', fontSize: '18px', fontWeight: 'bold' }}>爬虫监控系统</div>
        <Button onClick={handleLogout} type="text" style={{ color: '#fff' }}>退出</Button>
      </Header>
      <Layout>
        <Sider width={200} className="site-layout-background">
          <Menu
            mode="inline"
            selectedKeys={[currentView]}
            onClick={({ key }) => setCurrentView(key)}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
          />
        </Sider>
        <Layout style={{ padding: '24px' }}>
          <Content className="site-layout-background" style={{ padding: 24, margin: 0, minHeight: 280 }}>
            {currentView === 'dashboard' && <DashboardView tasks={tasks} results={results} />}
            {currentView === 'sites' && <SitesView sites={sites} onAddSite={addSite} />}
            {currentView === 'keywords' && <KeywordsView keywords={keywords} onAddKeyword={addKeyword} />}
            {currentView === 'tasks' && <TasksView tasks={tasks} sites={sites} keywords={keywords} onAddTask={addTask} />}
            {currentView === 'results' && <ResultsView results={results} />}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

// 登录表单组件
const LoginForm = ({ onLogin, onRegister }) => {
  const [form] = Form.useForm();
  const [isRegister, setIsRegister] = useState(false);

  const onFinish = (values) => {
    if (isRegister) {
      onRegister(values);
    } else {
      onLogin(values);
    }
  };

  return (
    <Form
      form={form}
      name="login"
      initialValues={{ remember: true }}
      onFinish={onFinish}
      autoComplete="off"
    >
      <Form.Item name="email" rules={[{ required: true, message: '请输入邮箱!' }]}>
        <Input placeholder="邮箱" />
      </Form.Item>
      <Form.Item name="password" rules={[{ required: true, message: '请输入密码!' }]}>
        <Input.Password placeholder="密码" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit" block>
          {isRegister ? '注册' : '登录'}
        </Button>
      </Form.Item>
      <Form.Item>
        <Button type="link" block onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? '已有账户？点击登录' : '没有账户？点击注册'}
        </Button>
      </Form.Item>
    </Form>
  );
};

// 仪表板视图
const DashboardView = ({ tasks, results }) => {
  return (
    <div>
      <Row gutter={16}>
        <Col span={8}>
          <Card title="总任务数" bordered={false}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', textAlign: 'center' }}>{tasks.length}</div>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="总爬取结果数" bordered={false}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', textAlign: 'center' }}>{results.length}</div>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="今日新增结果" bordered={false}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', textAlign: 'center' }}>
              {results.filter(r => new Date(r.crawled_at).toDateString() === new Date().toDateString()).length}
            </div>
          </Card>
        </Col>
      </Row>
      
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="最近爬取结果" bordered={false}>
            <Table 
              dataSource={results.slice(0, 5)} 
              columns={[
                { title: '标题', dataIndex: 'title', key: 'title' },
                { title: '关键词', dataIndex: 'keyword_matched', key: 'keyword_matched' },
                { title: '抓取时间', dataIndex: 'crawled_at', key: 'crawled_at' }
              ]} 
              pagination={false}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

// 网站管理视图
const SitesView = ({ sites, onAddSite }) => {
  const [form] = Form.useForm();

  const columns = [
    { title: '网站名称', dataIndex: 'name', key: 'name' },
    { title: 'URL', dataIndex: 'url', key: 'url' },
    { title: '类型', dataIndex: 'site_type', key: 'site_type' },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', 
      render: (is_active) => is_active ? '激活' : '未激活' 
    }
  ];

  const onFinish = (values) => {
    onAddSite(values);
    form.resetFields();
  };

  return (
    <div>
      <Card title="添加新监控网站" style={{ marginBottom: 24 }}>
        <Form form={form} layout="inline" onFinish={onFinish}>
          <Form.Item name="name" rules={[{ required: true, message: '请输入网站名称!' }]}>
            <Input placeholder="网站名称" />
          </Form.Item>
          <Form.Item name="url" rules={[{ required: true, message: '请输入网站URL!' }]}>
            <Input placeholder="网站URL" />
          </Form.Item>
          <Form.Item name="site_type">
            <Select placeholder="网站类型" style={{ width: 120 }}>
              <Option value="news">新闻</Option>
              <Option value="forum">论坛</Option>
              <Option value="blog">博客</Option>
              <Option value="general">通用</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">添加网站</Button>
          </Form.Item>
        </Form>
      </Card>
      
      <Card title="监控网站列表">
        <Table dataSource={sites} columns={columns} rowKey="id" />
      </Card>
    </div>
  );
};

// 关键词管理视图
const KeywordsView = ({ keywords, onAddKeyword }) => {
  const [form] = Form.useForm();

  const columns = [
    { title: '关键词', dataIndex: 'keyword', key: 'keyword' },
    { title: '分类', dataIndex: 'category', key: 'category' },
    { title: '优先级', dataIndex: 'priority', key: 'priority' },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', 
      render: (is_active) => is_active ? '激活' : '未激活' 
    }
  ];

  const onFinish = (values) => {
    onAddKeyword(values);
    form.resetFields();
  };

  return (
    <div>
      <Card title="添加新监控关键词" style={{ marginBottom: 24 }}>
        <Form form={form} layout="inline" onFinish={onFinish}>
          <Form.Item name="keyword" rules={[{ required: true, message: '请输入关键词!' }]}>
            <Input placeholder="关键词" />
          </Form.Item>
          <Form.Item name="category">
            <Select placeholder="分类" style={{ width: 120 }}>
              <Option value="general">通用</Option>
              <Option value="business">商业</Option>
              <Option value="technology">技术</Option>
              <Option value="health">健康</Option>
            </Select>
          </Form.Item>
          <Form.Item name="priority">
            <Select placeholder="优先级" style={{ width: 80 }}>
              <Option value={1}>1</Option>
              <Option value={2}>2</Option>
              <Option value={3}>3</Option>
              <Option value={4}>4</Option>
              <Option value={5}>5</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">添加关键词</Button>
          </Form.Item>
        </Form>
      </Card>
      
      <Card title="监控关键词列表">
        <Table dataSource={keywords} columns={columns} rowKey="id" />
      </Card>
    </div>
  );
};

// 任务管理视图
const TasksView = ({ tasks, sites, keywords, onAddTask }) => {
  const [form] = Form.useForm();

  const columns = [
    { title: '任务名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description' },
    { title: '频率', dataIndex: 'frequency', key: 'frequency' },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', 
      render: (is_active) => is_active ? '激活' : '未激活' 
    },
    { title: '上次运行', dataIndex: 'last_run', key: 'last_run' }
  ];

  const onFinish = (values) => {
    onAddTask(values);
    form.resetFields();
  };

  return (
    <div>
      <Card title="添加新爬虫任务" style={{ marginBottom: 24 }}>
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="name" label="任务名称" rules={[{ required: true, message: '请输入任务名称!' }]}>
                <Input placeholder="任务名称" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="frequency" label="执行频率" rules={[{ required: true, message: '请选择执行频率!' }]}>
                <Select placeholder="执行频率">
                  <Option value="PT1H">每小时</Option>
                  <Option value="PT6H">每6小时</Option>
                  <Option value="P1D">每天</Option>
                  <Option value="P7D">每周</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="description" label="描述">
                <Input placeholder="任务描述" />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="site_ids" label="监控网站" rules={[{ required: true, message: '请选择监控网站!' }]}>
                <Select mode="multiple" placeholder="选择监控网站">
                  {sites.map(site => (
                    <Option key={site.id} value={site.id}>{site.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="keyword_ids" label="监控关键词" rules={[{ required: true, message: '请选择监控关键词!' }]}>
                <Select mode="multiple" placeholder="选择监控关键词">
                  {keywords.map(keyword => (
                    <Option key={keyword.id} value={keyword.id}>{keyword.keyword}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item>
            <Button type="primary" htmlType="submit">添加任务</Button>
          </Form.Item>
        </Form>
      </Card>
      
      <Card title="爬虫任务列表">
        <Table dataSource={tasks} columns={columns} rowKey="id" />
      </Card>
    </div>
  );
};

// 结果展示视图
const ResultsView = ({ results }) => {
  const columns = [
    { title: '标题', dataIndex: 'title', key: 'title', render: (text, record) => <a href={record.url} target="_blank" rel="noopener noreferrer">{text}</a> },
    { title: '关键词', dataIndex: 'keyword_matched', key: 'keyword_matched' },
    { title: '发布日期', dataIndex: 'published_at', key: 'published_at' },
    { title: '抓取日期', dataIndex: 'crawled_at', key: 'crawled_at' },
    { title: '摘要', dataIndex: 'summary', key: 'summary' }
  ];

  return (
    <Card title="爬取结果">
      <Table 
        dataSource={results} 
        columns={columns} 
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />
    </Card>
  );
};

export default App;